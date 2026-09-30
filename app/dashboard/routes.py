from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from app.redis.client import redis_client
from app.ml.detector_service import DetectorService
from app.redis.security_events import get_security_events
from app.redis.client_state import get_client_state


router = APIRouter()

detector_service = DetectorService()


@router.get("/dashboard/data")
async def dashboard_data():

    clients = []

    keys = redis_client.scan_iter(
        match="request_features:*"
    )

    for key in keys:

        if isinstance(key, bytes):
            key = key.decode()

        client_ip = key.replace(
            "request_features:",
            ""
        )

        try:
            result = detector_service.analyze(client_ip)

            # Check cached security state first
            state = get_client_state(client_ip)

            if state:
                decision = state["decision"]

                # Use cached score if available
                if state.get("score") is not None:
                    if result["anomaly"]:
                        result["anomaly"]["score"] = state["score"]
                    else:
                        result["anomaly"] = {
                            "score": state["score"],
                            "is_anomaly": decision != "ALLOW"
                        }
            else:
                decision = result["decision"]

            clients.append({
                "client_ip": client_ip,
                "decision": decision,
                "features": result["features"],
                "anomaly": result["anomaly"]
            })

        except Exception as e:
            print(
                f"Dashboard error for {client_ip}: {e}"
            )

    return {
        "clients": clients
    }

    
@router.get("/dashboard/events")
async def dashboard_events():

    return {
        "events": get_security_events(50)
    }


@router.get(
    "/dashboard",
    response_class=HTMLResponse
)
async def dashboard():

    return """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>API GuardFlow Dashboard</title>

    <style>

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #0f1117;
            color: #e6e6e6;
        }

        .header {
            padding: 24px 40px;
            border-bottom: 1px solid #2a2d35;
        }

        .header h1 {
            margin: 0;
            font-size: 28px;
        }

        .header p {
            margin-top: 8px;
            color: #9da3ae;
        }

        .container {
            padding: 30px 40px;
        }

        .stats {
            display: grid;
            grid-template-columns:
                repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }

        .card {
            background: #181b23;
            border: 1px solid #2a2d35;
            border-radius: 12px;
            padding: 20px;
        }

        .card-title {
            color: #9da3ae;
            font-size: 14px;
        }

        .card-value {
            font-size: 30px;
            font-weight: bold;
            margin-top: 10px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            background: #181b23;
            border-radius: 12px;
            overflow: hidden;
        }

        th,
        td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #2a2d35;
        }

        th {
            color: #9da3ae;
            font-size: 13px;
        }

        .decision {
            font-weight: bold;
        }

        .ALLOW {
            color: #55d68a;
        }

        .THROTTLE {
            color: #f4c95d;
        }

        .BLOCK {
            color: #ff6b6b;
        }

        .normal {
            color: #55d68a;
        }

        .anomaly {
            color: #ff6b6b;
        }

        .empty {
            padding: 30px;
            text-align: center;
            color: #9da3ae;
        }
        
        .section-title {
            margin-top: 35px;
            margin-bottom: 15px;
            font-size: 18px;
            color: #e6e6e6;
        }
        
        .event-table {
            margin-bottom: 30px;
        }
        
        .event-BLOCK {
            color: #ff6b6b;
            font-weight: bold;
        }
        
        .event-THROTTLE {
            color: #f4c95d;
            font-weight: bold;
        }
        
        .event-ALLOW {
            color: #55d68a;
            font-weight: bold;
        }

        @media (max-width: 900px) {
            .stats {
                grid-template-columns:
                    repeat(2, 1fr);
            }
        }

    </style>

</head>

<body>

    <div class="header">

        <h1>API GuardFlow</h1>

        <p>
            Adaptive API rate limiting and
            behavioral abuse detection
        </p>

    </div>


    <div class="container">

        <div class="stats">

            <div class="card">
                <div class="card-title">
                    Clients
                </div>

                <div
                    class="card-value"
                    id="clients"
                >
                    0
                </div>
            </div>


            <div class="card">
                <div class="card-title">
                    Allowed
                </div>

                <div
                    class="card-value normal"
                    id="allowed"
                >
                    0
                </div>
            </div>


            <div class="card">
                <div class="card-title">
                    Throttled
                </div>

                <div
                    class="card-value"
                    id="throttled"
                >
                    0
                </div>
            </div>


            <div class="card">
                <div class="card-title">
                    Blocked
                </div>

                <div
                    class="card-value anomaly"
                    id="blocked"
                >
                    0
                </div>
            </div>

        </div>


        <table>

            <thead>

                <tr>
                    <th>Client IP</th>
                    <th>Requests/min</th>
                    <th>Unique Paths</th>
                    <th>Error Rate</th>
                    <th>Path Entropy</th>
                    <th>ML Score</th>
                    <th>Status</th>
                </tr>

            </thead>

            <tbody id="client-table">

            </tbody>

        </table>
        
        <div class="section-title">
            Recent Security Events
        </div>

        <table class="event-table">

            <thead>
                <tr>
                    <th>Time</th>
                    <th>Client IP</th>
                    <th>Decision</th>
                    <th>ML Score</th>
                    <th>Requests/min</th>
                    <th>Unique Paths</th>
                    <th>Error Rate</th>
                </tr>
            </thead>

            <tbody id="event-table">

            </tbody>

        </table>

    </div>


    <script>

        async function loadDashboard() {

            try {

                const response =
                    await fetch("/dashboard/data");

                const data =
                    await response.json();

                const clients =
                    data.clients;
                
                const eventsResponse =
                    await fetch("/dashboard/events");

                const eventsData =
                    await eventsResponse.json();

                const events =
                    eventsData.events || [];

                document.getElementById(
                    "clients"
                ).textContent = clients.length;


                let allowed = 0;
                let throttled = 0;
                let blocked = 0;


                const table =
                    document.getElementById(
                        "client-table"
                    );

                table.innerHTML = "";


                if (clients.length === 0) {

                    table.innerHTML = `
                        <tr>
                            <td
                                colspan="7"
                                class="empty"
                            >
                                No client traffic yet
                            </td>
                        </tr>
                    `;

                    return;
                }


                clients.forEach(client => {

                    if (client.decision === "ALLOW") {
                        allowed++;
                    }

                    if (client.decision === "THROTTLE") {
                        throttled++;
                    }

                    if (client.decision === "BLOCK") {
                        blocked++;
                    }


                    const features =
                        client.features || {};

                    const anomaly =
                        client.anomaly;


                    const score =
                        anomaly
                            ? anomaly.score.toFixed(4)
                            : "N/A";


                    const row =
                        document.createElement("tr");


                    row.innerHTML = `

                        <td>
                            ${client.client_ip}
                        </td>

                        <td>
                            ${
                                features.requests_per_minute
                                    ?? 0
                            }
                        </td>

                        <td>
                            ${
                                features.unique_paths
                                    ?? 0
                            }
                        </td>

                        <td>
                            ${
                                (
                                    (
                                        features.error_rate
                                        ?? 0
                                    ) * 100
                                ).toFixed(1)
                            }%
                        </td>

                        <td>
                            ${
                                features.path_entropy
                                    ?? 0
                            }
                        </td>

                        <td>
                            ${score}
                        </td>

                        <td
                            class="decision
                            ${client.decision}"
                        >
                            ${client.decision}
                        </td>

                    `;


                    table.appendChild(row);

                });
                
                                const eventTable =
                    document.getElementById("event-table");

                eventTable.innerHTML = "";

                if (events.length === 0) {

                    eventTable.innerHTML = `
                        <tr>
                            <td
                                colspan="7"
                                class="empty"
                            >
                                No security events yet
                            </td>
                        </tr>
                    `;

                } else {

                    events.forEach(event => {

                        const row =
                            document.createElement("tr");

                        const time =
                            new Date(
                                event.timestamp * 1000
                            ).toLocaleTimeString();

                        const score =
                            event.score !== null
                                ? Number(event.score).toFixed(4)
                                : "N/A";

                        const errorRate =
                            (
                                (event.error_rate ?? 0) * 100
                            ).toFixed(1);

                        row.innerHTML = `

                            <td>
                                ${time}
                            </td>

                            <td>
                                ${event.client_ip}
                            </td>

                            <td
                                class="event-${event.decision}"
                            >
                                ${event.decision}
                            </td>

                            <td>
                                ${score}
                            </td>

                            <td>
                                ${event.requests_per_minute ?? 0}
                            </td>

                            <td>
                                ${event.unique_paths ?? 0}
                            </td>

                            <td>
                                ${errorRate}%
                            </td>

                        `;

                        eventTable.appendChild(row);

                    });

                }


                document.getElementById(
                    "allowed"
                ).textContent = allowed;


                document.getElementById(
                    "throttled"
                ).textContent = throttled;


                document.getElementById(
                    "blocked"
                ).textContent = blocked;

            }

            catch (error) {

                console.error(
                    "Dashboard error:",
                    error
                );

            }

        }


        loadDashboard();

        setInterval(
            loadDashboard,
            3000
        );

    </script>

</body>

</html>
"""