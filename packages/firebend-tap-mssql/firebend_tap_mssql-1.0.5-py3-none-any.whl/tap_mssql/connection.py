#!/usr/bin/env python3

import backoff

import pyodbc

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

import singer
import ssl

from urllib.parse import quote_plus

LOGGER = singer.get_logger()


@backoff.on_exception(backoff.expo, pyodbc.Error, max_tries=5, factor=2)
def connect_with_backoff(connection):
    warnings = []
    with connection.cursor() as cur:
        if warnings:
            LOGGER.info(
                (
                    "Encountered non-fatal errors when configuring session that could "
                    "impact performance:"
                )
            )
        for w in warnings:
            LOGGER.warning(w)

    return connection


def decode_sketchy_utf16(raw_bytes):
    """Updates the output handling where malformed unicode is received from MSSQL"""
    s = raw_bytes.decode("utf-16le", "ignore")
    try:
        n = s.index("\u0000")
        s = s[:n]  # respect null terminator
    except ValueError:
        pass
    return s


def modify_ouput_converter(conn):

    prev_converter = conn.connection.get_output_converter(pyodbc.SQL_WVARCHAR)
    conn.connection.add_output_converter(pyodbc.SQL_WVARCHAR, decode_sketchy_utf16)

    return prev_converter


def revert_ouput_converter(conn, prev_converter):
    conn.connection.add_output_converter(pyodbc.SQL_WVARCHAR, prev_converter)


def get_azure_sql_engine(config) -> Engine:
    """The All-Purpose SQL connection object for the Azure Data Warehouse."""

    conn_values = {
        "prefix": "mssql+pyodbc://",
        "username": config["user"],
        "password": quote_plus(config["password"]),
        "port": config.get("port", "1433"),
        "host": config["host"],
        "driver": "ODBC+Driver+17+for+SQL+Server",
        "database": config["database"],
    }

    conn_values["authentication"] = "SqlPassword"
    raw_conn_string = "{prefix}{username}:{password}@{host}:\
{port}/{database}?driver={driver}&Authentication={authentication}&\
autocommit=True&IntegratedSecurity=False"

    engine = create_engine(raw_conn_string.format(**conn_values))
    return engine
