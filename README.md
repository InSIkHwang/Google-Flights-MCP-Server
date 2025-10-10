# Google Flights MCP Server

This MCP server provides tools to interact with Google Flights data using the bundled `fast_flights` library.

## Features

Provides the following MCP tools:

### Airline Filtering

The `find_all_flights_in_range_v2` tool supports filtering flights by specific airlines using the `airline_filter` parameter. This feature:

- Uses case-insensitive partial matching (e.g., "delta" will match "Delta Air Lines")
- Filters results after fetching from Google Flights
- Works with both `return_cheapest_only` and full results modes
- Example: `"airline_filter": "Delta"` will only return flights operated by Delta Air Lines

- **`get_flights_on_date`**: Fetches available one-way flights for a specific date between two airports.
  - Args: `origin` (str), `destination` (str), `date` (str, YYYY-MM-DD), `adults` (int, optional), `seat_type` (str, optional), `return_cheapest_only` (bool, optional, default `False`).
- **`get_round_trip_flights`**: Fetches available round-trip flights for specific departure and return dates.
  - Args: `origin` (str), `destination` (str), `departure_date` (str, YYYY-MM-DD), `return_date` (str, YYYY-MM-DD), `adults` (int, optional), `seat_type` (str, optional), `return_cheapest_only` (bool, optional, default `False`).
- **`find_all_flights_in_range_v2`**: Finds available round-trip flights within a specified date range. Can optionally return only the cheapest flight found for each date pair. Supports airline filtering.
  - Args: `origin` (str), `destination` (str), `start_date_str` (str, YYYY-MM-DD), `end_date_str` (str, YYYY-MM-DD), `min_stay_days` (int, optional), `max_stay_days` (int, optional), `adults` (int, optional), `seat_type` (str, optional), `return_cheapest_only` (bool, optional, default `False`), `airline_filter` (str, optional) - Filter flights by specific airline name using case-insensitive partial matching.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/opspawn/Google-Flights-MCP-Server.git
    cd Google-Flights-MCP-Server
    ```
2.  **가상환경 생성 (권장):**
    ```cmd
    python -m venv .venv
    cmd .venv\Scripts\activate
    ```
3.  **의존성 설치:**
    ```cmd
    pip install -r requirements.txt
    ```
4.  **Playwright 브라우저 설치 (`fast_flights`에 필요):**
    ```cmd
    playwright install
    ```

## 서버 실행

Python으로 서버를 직접 실행할 수 있습니다:

```cmd
python server.py
```

The server uses STDIO transport by default.

## Integrating with MCP Clients (e.g., Cline, Claude Desktop)

Add the server to your MCP client's configuration file. Example for `cline_mcp_settings.json` or `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "google-flights": {
      "command": "/path/to/your/.venv/bin/python", // Use absolute path to venv python
      "args": [
        "/absolute/path/to/flight_mcp_server/server.py" // Use absolute path to server script
      ],
      "env": {},
      "disabled": false,
      "autoApprove": []
    }
    // ... other servers
  }
}
```

**Important:** Replace the paths in `command` and `args` with the absolute paths to your virtual environment's Python executable and the `server.py` script on your system.

## Notes

- This server bundles the `fast_flights` library (originally from [https://github.com/AWeirdDev/flights](https://github.com/AWeirdDev/flights)) for its core flight scraping functionality. Please refer to the included `LICENSE` file for its terms.
- Flight scraping can sometimes be unreliable or slow depending on Google Flights changes and network conditions. The tools include basic error handling.
- The `find_all_flights_in_range_v2` tool can be resource-intensive as it checks many date combinations.
- **Airline filtering**: The airline filter works by matching airline names in the flight results. Common airline names include "Delta", "American", "United", "Southwest", "JetBlue", etc. Partial matching is supported (e.g., "Delta" will match "Delta Air Lines").
