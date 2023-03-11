#!/usr/bin/env python3
import logging
import textwrap
import socket
from typing import Any
from yaml import load
import streamlit as st

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


PROGRESS_TEXT = "Scanning hosts. Please wait"


def check_tcp_port_xmas(dst_ip: str, dst_port: int) -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex((dst_ip, dst_port))
            if result == 0:
                return "Open"
            else:
                return "Closed"
    except (TypeError, PermissionError) as perm_err:
        logging.exception(perm_err)
        return "Error"


def load_config(stream) -> Any:
    return load(stream, Loader=Loader)


if __name__ == "__main__":
    st.title("TCP Port scanner")
    st.markdown(textwrap.dedent("""
    Simple TCP/ IP port scanner.
"""))

    st.file_uploader(
        "Please provide the configuration file to load",
        accept_multiple_files=False,
        key="portscan_config"
    )
    if st.session_state['portscan_config']:
        yaml = load_config(st.session_state['portscan_config'])
        hosts_details = yaml['hosts']
        chunks = len(hosts_details)
        try:
            data_load_state = st.text('Preparing to scan...')
            with st.spinner(f"Total hosts to scan: {chunks}"):
                ip = None
                for host in hosts_details:
                    host_name = host['name'].strip()
                    ports = host['ports']
                    try:
                        ip = socket.gethostbyname(host_name)
                        for port in ports:
                            status = check_tcp_port_xmas(dst_ip=ip, dst_port=port)
                            data_load_state.text(f"Processing: {host_name}({ip}):{port}, status={status}")
                            if status == "Open":
                                st.info(f"{host_name}:{port}, status={status}")
                            elif status == "Closed":
                                st.warning(f"{host_name}:{port}, status={status}")
                            else:
                                st.error(f"{host_name}:{port}, status={status}")
                    except TypeError as os_err:
                        raise
            data_load_state.success(f"Finished scanning {chunks} hosts")
        except (KeyError, ValueError, OSError, TypeError) as err:
            st.error(hosts_details)
            st.exception(err)
    else:
        st.warning("Please load a PortTester configuration file to proceed")
