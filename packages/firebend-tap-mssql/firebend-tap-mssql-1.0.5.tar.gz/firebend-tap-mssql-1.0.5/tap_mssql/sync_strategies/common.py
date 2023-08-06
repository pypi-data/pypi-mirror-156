#!/usr/bin/env python3
# pylint: disable=too-many-arguments,duplicate-code,too-many-locals

import copy
import datetime
import singer
import time
import uuid
from typing import List

import singer.metrics as metrics
from singer import metadata
from singer import utils

LOGGER = singer.get_logger()


def escape(identifier: str) -> str:
    return "[{}]".format(identifier.replace("]", "]]"))


def set_schema_mapping(config, stream):
    schema_mapping = config.get("include_schemas_in_destination_stream_name")

    if schema_mapping:
        stream = stream.replace("-", "_")
    return stream


def generate_tap_stream_id(table_schema, table_name):
    return table_schema + "-" + table_name


def get_stream_version(tap_stream_id, state):
    stream_version = singer.get_bookmark(state, tap_stream_id, "version")

    if stream_version is None:
        stream_version = int(time.time() * 1000)

    return stream_version


def stream_is_selected(stream):
    md_map = metadata.to_map(stream.metadata)
    selected_md = metadata.get(md_map, (), "selected")

    return selected_md


def property_is_selected(stream, property_name):
    md_map = metadata.to_map(stream.metadata)
    return singer.should_sync_field(
        metadata.get(md_map, ("properties", property_name), "inclusion"),
        metadata.get(md_map, ("properties", property_name), "selected"),
        True,
    )


def get_is_view(catalog_entry):
    md_map = metadata.to_map(catalog_entry.metadata)

    return md_map.get((), {}).get("is-view")


def get_database_name(catalog_entry):
    md_map = metadata.to_map(catalog_entry.metadata)

    return md_map.get((), {}).get("database-name")


def get_key_properties(catalog_entry):
    catalog_metadata = metadata.to_map(catalog_entry.metadata)
    stream_metadata = catalog_metadata.get((), {})

    is_view = get_is_view(catalog_entry)

    if is_view:
        key_properties = stream_metadata.get("view-key-properties", [])
    else:
        key_properties = stream_metadata.get("table-key-properties", [])

    return key_properties


def map_sql_columns(catalog_entry, columns) -> List[str]:
    md_map = metadata.to_map(catalog_entry.metadata)
    mapped_columns = []
    for idx, column in enumerate(columns):
        property_type = md_map.get(("properties", columns[idx])).get("sql-datatype")
        if property_type == "timestamp":
            mapped_columns.append(
                f"CAST({escape(column)} AS BIGINT) AS {escape(column)}"
            )
        else:
            mapped_columns.append(escape(column))

    return mapped_columns


def generate_select_sql(catalog_entry, columns):
    database_name = get_database_name(catalog_entry)
    escaped_db = escape(database_name)
    escaped_table = escape(catalog_entry.table)
    mapped_columns = map_sql_columns(catalog_entry, columns)

    select_sql = "SELECT {} FROM {}.{}".format(
        ",".join(mapped_columns), escaped_db, escaped_table
    )

    # escape percent signs
    select_sql = select_sql.replace("%", "%%")
    return select_sql


def row_to_singer_record(
    catalog_entry, version, table_stream, row, columns, time_extracted
):
    row_to_persist = ()
    md_map = metadata.to_map(catalog_entry.metadata)
    md_map[("properties", "_sdc_deleted_at")] = {
        "sql-datatype": "datetime"  # maybe datetimeoffset??
    }
    for idx, elem in enumerate(row):
        # property_type = catalog_entry.schema.properties[columns[idx]].type
        property_type = md_map.get(("properties", columns[idx])).get("sql-datatype")
        if isinstance(elem, datetime.datetime):
            if elem.tzinfo:
                row_to_persist += (elem.isoformat(),)
            else:
                row_to_persist += (elem.isoformat() + "+00:00",)

        elif isinstance(elem, datetime.date):
            row_to_persist += (elem.isoformat() + "T00:00:00+00:00",)

        elif isinstance(elem, datetime.time):
            row_to_persist += (elem.isoformat() + "+00:00",)

        elif isinstance(elem, datetime.timedelta):
            epoch = datetime.datetime.utcfromtimestamp(0)
            timedelta_from_epoch = epoch + elem
            row_to_persist += (timedelta_from_epoch.isoformat() + "+00:00",)

        elif isinstance(elem, bytes):
            if property_type in ["binary", "varbinary"]:
                # Convert binary byte array to hex string‘
                hex_representation = f"0x{elem.hex().upper()}"
                row_to_persist += (hex_representation,)
            else:
                # for BIT value, treat 0 as False and anything else as True
                boolean_representation = elem != b"\x00"
                row_to_persist += (boolean_representation,)

        elif "boolean" in property_type or property_type == "boolean":
            if elem is None:
                boolean_representation = None
            elif elem == 0:
                boolean_representation = False
            else:
                boolean_representation = True
            row_to_persist += (boolean_representation,)
        elif isinstance(elem, uuid.UUID):
            row_to_persist += (str(elem),)
        else:
            row_to_persist += (elem,)
    rec = dict(zip(columns, row_to_persist))

    return singer.RecordMessage(
        stream=table_stream,
        record=rec,
        version=version,
        time_extracted=time_extracted,
    )


def whitelist_bookmark_keys(bookmark_key_set, tap_stream_id, state):
    for bk in [
        non_whitelisted_bookmark_key
        for non_whitelisted_bookmark_key in state.get("bookmarks", {})
        .get(tap_stream_id, {})
        .keys()
        if non_whitelisted_bookmark_key not in bookmark_key_set
    ]:
        singer.clear_bookmark(state, tap_stream_id, bk)


def sync_query(
    cursor,
    catalog_entry,
    state,
    select_sql,
    columns,
    stream_version,
    table_stream,
    params,
):
    replication_key = singer.get_bookmark(
        state, catalog_entry.tap_stream_id, "replication_key"
    )

    # query_string = cursor.mogrify(select_sql, params)

    time_extracted = utils.now()
    if len(params) == 0:
        results = cursor.execute(select_sql)
    else:
        results = cursor.execute(select_sql, params["replication_key_value"])
    row = results.fetchone()
    rows_saved = 0

    database_name = get_database_name(catalog_entry)

    with metrics.record_counter(None) as counter:
        counter.tags["database"] = database_name
        counter.tags["table"] = catalog_entry.table

        while row:
            counter.increment()
            rows_saved += 1
            record_message = row_to_singer_record(
                catalog_entry,
                stream_version,
                table_stream,
                row,
                columns,
                time_extracted,
            )
            singer.write_message(record_message)
            md_map = metadata.to_map(catalog_entry.metadata)
            stream_metadata = md_map.get((), {})
            replication_method = stream_metadata.get("replication-method")

            if replication_method in {"FULL_TABLE", "LOG_BASED"}:
                key_properties = get_key_properties(catalog_entry)

                max_pk_values = singer.get_bookmark(
                    state, catalog_entry.tap_stream_id, "max_pk_values"
                )

                if max_pk_values:
                    last_pk_fetched = {
                        k: v
                        for k, v in record_message.record.items()
                        if k in key_properties
                    }

                    state = singer.write_bookmark(
                        state,
                        catalog_entry.tap_stream_id,
                        "last_pk_fetched",
                        last_pk_fetched,
                    )

            elif replication_method == "INCREMENTAL":
                if replication_key is not None:
                    state = singer.write_bookmark(
                        state,
                        catalog_entry.tap_stream_id,
                        "replication_key",
                        replication_key,
                    )

                    state = singer.write_bookmark(
                        state,
                        catalog_entry.tap_stream_id,
                        "replication_key_value",
                        record_message.record[replication_key],
                    )
            if rows_saved % 1000 == 0:
                singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))

            row = results.fetchone()

    singer.write_message(singer.StateMessage(value=copy.deepcopy(state)))
