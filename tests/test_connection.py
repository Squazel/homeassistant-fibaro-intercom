#!/usr/bin/env python3
"""
Manual test script for FIBARO Intercom WebSocket connection.
Run this to test connectivity independently of Home Assistant.
"""

import asyncio
import json
import os
import ssl
import websockets


async def test_intercom_connection():
    """Test connection to FIBARO Intercom."""

    # Get connection details from environment variables or use defaults
    HOST = os.getenv("FIBARO_HOST", "YOUR_INTERCOM_IP")  # e.g., "192.168.1.100"
    PORT = 8081  # Fixed port for FIBARO Intercom WebSocket API
    USERNAME = os.getenv("FIBARO_USERNAME", "YOUR_USERNAME")
    PASSWORD = os.getenv("FIBARO_PASSWORD", "YOUR_PASSWORD")

    # Validate that credentials were provided
    if (
        HOST == "YOUR_INTERCOM_IP"
        or USERNAME == "YOUR_USERNAME"
        or PASSWORD == "YOUR_PASSWORD"
    ):
        print("❌ Please set environment variables or edit the script:")
        print("   FIBARO_HOST=your_intercom_ip")
        print("   FIBARO_USERNAME=your_username")
        print("   FIBARO_PASSWORD=your_password")
        print("\n   Example (PowerShell):")
        print("   $env:FIBARO_HOST='192.168.1.100'")
        print("   $env:FIBARO_USERNAME='admin'")
        print("   $env:FIBARO_PASSWORD='your_password'")
        print("   python tests/test_connection.py")
        return False

    uri = f"wss://{HOST}:{PORT}/wsock"

    print(f"Testing connection to: {uri}")
    print(f"Username: {USERNAME}")
    print("-" * 50)

    try:
        # Create SSL context (disable certificate verification for testing)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        print("🔗 Attempting WebSocket connection...")

        async with websockets.connect(
            uri, ssl=ssl_context, ping_timeout=10
        ) as websocket:
            print("✅ WebSocket connection established!")

            # Send login request
            login_request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "com.fibaro.intercom.account.login",
                "params": {
                    "user": USERNAME,
                    "pass": PASSWORD,
                },
            }

            print("🔐 Sending login request...")
            await websocket.send(json.dumps(login_request))

            # Wait for response
            print("⏳ Waiting for login response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=10)
            data = json.loads(response)

            print("📨 Received response:")
            print(json.dumps(data, indent=2))

            if "error" in data:
                print(f"❌ Login failed: {data['error']}")
                return False

            if "result" in data and "token" in data["result"]:
                print("✅ Login successful!")
                print(f"🎫 Token received: {data['result']['token'][:20]}...")
                return True
            else:
                print("❌ Invalid login response format")
                return False

    except websockets.exceptions.InvalidURI as e:
        print(f"❌ Invalid URI: {e}")
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
    except ConnectionRefusedError as e:
        print(f"❌ Connection refused: {e}")
        print("💡 Check if the intercom is reachable and port 8081 is open")
    except asyncio.TimeoutError:
        print("❌ Connection timeout")
        print("💡 Check network connectivity and firewall settings")
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

    return False


if __name__ == "__main__":
    print("FIBARO Intercom Connection Test")
    print("=" * 50)
    print("💡 Set environment variables or edit the script with your intercom details")
    print("   Environment variables: FIBARO_HOST, FIBARO_USERNAME, FIBARO_PASSWORD")
    print("")

    # Update the connection details above before running
    result = asyncio.run(test_intercom_connection())

    if result:
        print("\n🎉 Connection test PASSED!")
        print("   You can proceed with the Home Assistant integration setup.")
    else:
        print("\n💥 Connection test FAILED!")
        print("   Please check the troubleshooting steps in the README.")
