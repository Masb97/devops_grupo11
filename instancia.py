"""ID de la instancia EC2 vía IMDSv2 (en Amazon Linux 2023 IMDSv1 viene apagado)."""
import socket
import urllib.request

IMDS = "http://169.254.169.254/latest"


def leer_instance_id(timeout=1.0):
    try:
        req = urllib.request.Request(
            f"{IMDS}/api/token", method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "300"},
        )
        token = urllib.request.urlopen(req, timeout=timeout).read().decode()
        req = urllib.request.Request(
            f"{IMDS}/meta-data/instance-id",
            headers={"X-aws-ec2-metadata-token": token},
        )
        return urllib.request.urlopen(req, timeout=timeout).read().decode()
    except Exception:
        # Fuera de EC2 (tu portátil) no hay servicio de metadatos.
        return f"local-{socket.gethostname()}"


INSTANCE_ID = leer_instance_id()
