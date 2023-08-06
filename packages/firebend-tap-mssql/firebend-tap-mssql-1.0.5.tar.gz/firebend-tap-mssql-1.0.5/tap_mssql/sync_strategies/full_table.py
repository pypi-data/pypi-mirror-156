#!/usr/bin/env python3
# pylint: disable=duplicate-code,too-many-locals,simplifiable-if-expression

import copy
import singer
from singer import metadata

import tap_mssql.sync_strategies.common as common

from tap_mssql.connection import (
    connect_with_backoff,
    get_azure_sql_engine,
    modify_ouput_converter,
    revert_ouput_converter,
)

LOGGER = singer.get_logger()


def generate_bookmark_keys(catalog_entry):
    md_map = metadata.to_map(catalog_entry.metadata)
    stream_metadata = md_map.get((), {})
    replication_method = stream_metadata.get("replication-method")

    base_bookmark_keys = {
        "last_pk_fetched",
        "max_pk_values",
        "version",
        "initial_full_table_complete",
    }

    bookmark_keys = base_bookmark_keys

    return bookmark_keys


def sync_table(mssql_conn, config, catalog_entry, state, columns, stream_version):
    mssql_conn = get_azure_sql_engine(config)
    common.whitelist_bookmark_keys(
        generate_bookmark_keys(catalog_entry), catalog_entry.tap_stream_id, state
    )

    bookmark = state.get("bookmarks", {}).get(catalog_entry.tap_stream_id, {})
    version_exists = True if "version" in bookmark else False

    initial_full_table_complete = singer.get_bookmark(
        state, catalog_entry.tap_stream_id, "initial_full_table_complete"
    )

    state_version = singer.get_bookmark(state, catalog_entry.tap_stream_id, "version")

    table_stream = common.set_schema_mapping(config, catalog_entry.stream)

    activate_version_message = singer.ActivateVersionMessage(
        stream=table_stream, version=stream_version
    )

    # For the initial replication, emit an ACTIVATE_VERSION message
    # at the beginning so the records show up right away.
    if not initial_full_table_complete and not (
        version_exists and state_version is None
    ):
        singer.write_message(activate_version_message)

    with mssql_conn.connect() as open_conn:
        LOGGER.info("Generating select_sql")
        select_sql = common.generate_select_sql(catalog_entry, columns)

        params = {}

        common.sync_query(
            open_conn,
            catalog_entry,
            state,
            select_sql,
            columns,
            stream_version,
            table_stream,
            params,
        )

    # clear max pk value and last pk fetched upon successful sync
    singer.clear_bookmark(state, catalog_entry.tap_stream_id, "max_pk_values")
    singer.clear_bookmark(state, catalog_entry.tap_stream_id, "last_pk_fetched")

    singer.write_message(activate_version_message)
