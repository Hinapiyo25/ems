"""WSGI entry point.

PyCharm: right-click this file -> Run 'app'.  VS Code: `python app.py`.
Production style: `flask --app app run`  or  `gunicorn "app:create_app()"`.

Environment variables (all optional):

    EMS_HOST    127.0.0.1 (default) or 0.0.0.0 to let other machines connect
    EMS_PORT    5000 by default
    EMS_DEBUG   1/0; defaults to on only for a local bind

Examples
--------
Local only (default):          python app.py
Share on the local network:    set EMS_HOST=0.0.0.0 && python app.py
Expose through a tunnel:       python app.py        (keep it on 127.0.0.1)
                               cloudflared tunnel --url http://127.0.0.1:5000
"""

import os
import socket

from app import create_app
from app.extensions import db

app = create_app()


@app.shell_context_processor
def _shell_context():
    """Expose the model layer in `flask shell`."""
    from app import models

    return {
        "db": db,
        "User": models.User,
        "Employee": models.Employee,
        "ShiftTemplate": models.ShiftTemplate,
        "Schedule": models.Schedule,
        "ShiftPreference": models.ShiftPreference,
        "LeaveRequest": models.LeaveRequest,
        "Attendance": models.Attendance,
        "EmployeeWorkingDay": models.EmployeeWorkingDay,
    }


def _lan_addresses():
    """Best-effort list of IPv4 addresses other devices could use."""
    addresses = set()
    hostname = socket.gethostname()
    candidates = [hostname, socket.getfqdn()]
    try:
        candidates.append(socket.gethostbyname(hostname))
    except OSError:
        pass
    for name in candidates:
        try:
            for info in socket.getaddrinfo(name, None, socket.AF_INET):
                ip = info[4][0]
                if not ip.startswith("127.") and not ip.startswith("169.254."):
                    addresses.add(ip)
        except OSError:
            continue
    return sorted(addresses)


def main():
    host = os.environ.get("EMS_HOST", "127.0.0.1").strip()
    port = int(os.environ.get("EMS_PORT", "5000"))

    debug_env = os.environ.get("EMS_DEBUG")
    local_only = host in ("127.0.0.1", "localhost")
    debug = (debug_env == "1") if debug_env is not None else local_only

    shared = host in ("0.0.0.0", "::", "")

    print("=" * 68)
    print(" EMS - Employee Management System")
    print("=" * 68)
    print(f" Local:   http://127.0.0.1:{port}/")
    if shared:
        addresses = _lan_addresses()
        if addresses:
            for ip in addresses:
                print(f" Network: http://{ip}:{port}/   <- share this on the same Wi-Fi")
        else:
            print(" Network: (could not detect a LAN address)")
        print("")
        print(" If others cannot connect: allow Python through the Windows Firewall")
        print(" (Control Panel > Windows Defender Firewall > Allow an app).")
    else:
        print(" Network: disabled (only this computer can connect).")
        print(" To share on the local network:  set EMS_HOST=0.0.0.0")
    if debug:
        print(" Debugger: ON (fine locally, do NOT expose it to the internet)")
    else:
        print(" Debugger: OFF")
    print("=" * 68, flush=True)

    app.run(host=host, port=port, debug=debug, use_reloader=debug)


if __name__ == "__main__":
    main()
