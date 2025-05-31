import httpx
import traceback

# Hardcoded credentials for Render (ensure this is secured in production)
RENDER_API_KEY = "rnd_GSVYe0xfbdhpwpK2XaLjZUAexvbh"
RENDER_SERVICE_ID = "srv-d090la15pdvs739vqerg"

RENDER_DEPLOY_ENDPOINT = f"https://api.render.com/v1/services/{RENDER_SERVICE_ID}/deploys"
HEADERS = {
    "Authorization": f"Bearer {RENDER_API_KEY}",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

async def trigger_manual_deploy():
    """
    Triggers a manual deployment of the specified Render service.
    It will pull the latest commit from the connected GitHub repo (e.g., main branch).
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(RENDER_DEPLOY_ENDPOINT, headers=HEADERS)

            try:
                json_data = response.json()
            except Exception:
                json_data = {"error": "Response is not valid JSON", "raw": response.text}

            if response.status_code != 201 and response.status_code != 200:
                return {
                    "status": "error",
                    "message": f"Unexpected status: {response.status_code}",
                    "details": json_data
                }

            return {
                "status": "success",
                "message": "Deployment triggered successfully.",
                "details": json_data
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "traceback": traceback.format_exc()
        }
