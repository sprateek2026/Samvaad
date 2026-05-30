from fastapi import HTTPException, Header
import os


async def verify_firebase_token(authorization: str | None = Header(None)):
    dev_mode = os.getenv("DEV_MODE", "true").lower() == "true"

    if dev_mode:
        if authorization and authorization.startswith("Bearer "):
            return {"uid": authorization[7:], "phone": "9876543210", "dev_mode": True}
        return {"uid": "dev-user-123", "phone": "9876543210", "dev_mode": True}

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = authorization.split(" ")[1]

    try:
        import firebase_admin
        from firebase_admin import credentials, auth

        if not os.path.exists("firebase-credentials.json"):
            raise HTTPException(status_code=500, detail="Firebase credentials not found. Set DEV_MODE=true to bypass.")

        cred = credentials.Certificate("firebase-credentials.json")
        try:
            firebase_admin.get_app()
        except ValueError:
            firebase_admin.initialize_app(cred)

        decoded = auth.verify_id_token(token)
        return {"uid": decoded["uid"], "phone": decoded.get("phone_number", "")}
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
