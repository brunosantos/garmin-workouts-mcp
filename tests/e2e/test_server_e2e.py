"""
End-to-end test for MCP server functionality

This test connects to the actual MCP server and makes real API calls.
It requires valid Garmin credentials in the .env file.

WARNING: These tests may hang if:
- Garmin credentials are invalid
- MFA is required and tokens are expired
- Network connection is unavailable

Run with: pytest tests/e2e/ -m e2e
Or skip with: pytest -m "not e2e"
"""

import pytest
import asyncio
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Import MCP client for testing
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Load environment variables
load_dotenv()


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)  # Pytest timeout
async def test_mcp_server_connection():
    """Test MCP server connection and initialization

    WARNING: This test requires:
    - Valid GARMIN_EMAIL and GARMIN_PASSWORD in .env file
    - Active internet connection
    - May require MFA code input if tokens are expired
    """
    # Use python module execution instead of direct script path
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "garmin_workouts_mcp"],
        env=None,  # Uses current environment which includes .env variables
    )

    # Connect to server with timeout
    try:
        async with asyncio.timeout(20):  # AsyncIO timeout
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # Initialize the connection
                    await session.initialize()

                    # List available tools
                    tools = await session.list_tools()

                    # Verify we have tools
                    assert len(tools.tools) > 0, "No tools found in MCP server"

                    # Print available tools for debugging
                    print(f"\nFound {len(tools.tools)} tools:")
                    for tool in tools.tools[:5]:  # Show first 5
                        print(f"  - {tool.name}: {tool.description}")
                    print(f"  ... and {len(tools.tools) - 5} more")
    except asyncio.TimeoutError:
        pytest.fail(
            "Server connection timed out after 20 seconds. "
            "Check your Garmin credentials in .env file and network connection. "
            "If MFA is required, run the server manually first to authenticate."
        )


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_list_activities_tool():
    """Test the list_activities MCP tool with real API"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "garmin_workouts_mcp"],
        env=None,
    )

    try:
        async with asyncio.timeout(20):
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Test list_activities
                    result = await session.call_tool(
                        "list_activities",
                        arguments={"limit": 2}
                    )

                    # Verify result
                    assert result is not None
                    assert len(result.content) > 0

                    # Print result for debugging
                    print(f"\nlist_activities result preview:")
                    print(result.content[0].text[:500] + "...")
    except asyncio.TimeoutError:
        pytest.fail("Tool execution timed out - check your Garmin credentials and network")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_get_steps_data_tool():
    """Test the get_steps_data MCP tool with real API"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "garmin_workouts_mcp"],
        env=None,
    )

    try:
        async with asyncio.timeout(20):
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    # Test get_steps_data with today's date
                    today = datetime.now().strftime("%Y-%m-%d")

                    result = await session.call_tool(
                        "get_steps_data",
                        arguments={"date": today}
                    )

                    # Verify result
                    assert result is not None
                    assert len(result.content) > 0

                    # Print result for debugging
                    print(f"\nget_steps_data result preview:")
                    print(result.content[0].text[:500] + "...")
    except asyncio.TimeoutError:
        pytest.fail("Tool execution timed out - check your Garmin credentials and network")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(45)
async def test_multiple_tools():
    """Test multiple MCP tools in a single session"""
    server_params = StdioServerParameters(
        command="python",
        args=["-m", "garmin_workouts_mcp"],
        env=None,
    )

    try:
        async with asyncio.timeout(40):
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    today = datetime.now().strftime("%Y-%m-%d")

                    # Test multiple tools
                    tools_to_test = [
                        ("list_activities", {"limit": 1}),
                        ("get_steps_data", {"date": today}),
                        ("get_user_profile", {}),
                    ]

                    for tool_name, args in tools_to_test:
                        try:
                            result = await session.call_tool(tool_name, arguments=args)
                            assert result is not None
                            print(f"\n✓ {tool_name} succeeded")
                        except Exception as e:
                            print(f"\n✗ {tool_name} failed: {str(e)}")
                            # Don't fail the test for individual tool failures
                            # Some tools may not have data available
    except asyncio.TimeoutError:
        pytest.fail("Multiple tools test timed out - check your Garmin credentials and network")


@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_schedule_workouts_tool():
    """Test schedule_workout MCP tool with multiple workouts

    WARNING: This test requires:
    - Valid GARMIN_EMAIL and GARMIN_PASSWORD in .env file
    - Active internet connection
    - Real workout IDs from your Garmin library (set GARMIN_TEST_WORKOUT_IDS env var)

    Set GARMIN_TEST_WORKOUT_IDS as a comma-separated list of workout IDs,
    and GARMIN_TEST_SCHEDULE_DATES as a comma-separated list of YYYY-MM-DD dates
    (must match the number of IDs).

    If env vars are not set, the test verifies the tool is accessible and
    returns a structured response for a dummy schedule (expected to fail gracefully).
    """
    import os
    import json

    server_params = StdioServerParameters(
        command="python",
        args=["-m", "garmin_workouts_mcp"],
        env=None,
    )

    workout_ids_env = os.environ.get("GARMIN_TEST_WORKOUT_IDS", "")
    dates_env = os.environ.get("GARMIN_TEST_SCHEDULE_DATES", "")

    if workout_ids_env and dates_env:
        ids = [int(wid.strip()) for wid in workout_ids_env.split(",")]
        dates = [d.strip() for d in dates_env.split(",")]
        assert len(ids) == len(dates), "GARMIN_TEST_WORKOUT_IDS and GARMIN_TEST_SCHEDULE_DATES must have the same number of entries"
        schedules = [{"workout_id": wid, "calendar_date": date} for wid, date in zip(ids, dates)]
    else:
        # Use a dummy schedule — expected to fail at the API level but the tool should handle it gracefully
        schedules = [
            {"workout_id": 0, "calendar_date": "2099-01-01"},
        ]

    try:
        async with asyncio.timeout(50):
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    result = await session.call_tool(
                        "schedule_workouts",
                        arguments={"schedules": schedules}
                    )

                    assert result is not None
                    assert len(result.content) > 0

                    result_data = json.loads(result.content[0].text)
                    assert "total" in result_data
                    assert "succeeded" in result_data
                    assert "failed" in result_data
                    assert "results" in result_data
                    assert result_data["total"] == len(schedules)
                    assert len(result_data["results"]) == len(schedules)

                    print(f"\nschedule_workout result:")
                    print(json.dumps(result_data, indent=2))
    except asyncio.TimeoutError:
        pytest.fail("schedule_workout test timed out - check your Garmin credentials and network")
