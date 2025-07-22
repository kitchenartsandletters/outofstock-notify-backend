import os
from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from fastapi.responses import Response
from app.supabase_client import insert_interest, supabase

router = APIRouter()

class InterestRequest(BaseModel):
    email: str
    product_id: int
    product_title: str
    isbn: str

@router.api_route("/interest", methods=["POST", "OPTIONS"])
async def create_interest(req: Request):
    if req.method == "OPTIONS":
        response = Response()
        response.headers["Access-Control-Allow-Origin"] = "https://www.kitchenartsandletters.com"
        response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    try:
        body = await req.json()
        request = InterestRequest(**body)
        result = insert_interest(
            email=request.email,
            product_id=request.product_id,
            product_title=request.product_title,
            isbn=request.isbn
        )
        return {"success": True, "data": result}
    except Exception as e:
        print("Error inserting interest:", e)
        raise HTTPException(status_code=500, detail="Failed to record interest.")

@router.get("/interest")
async def get_interest_entries(token: str = ""):
    if token != os.getenv("VITE_ADMIN_TOKEN"):
        raise HTTPException(status_code=403, detail="Invalid token")

    try:
        result = supabase.table("product_interest_requests").select("cr_id, product_title, isbn, product_id, email, created_at").order("created_at", desc=True).limit(100).execute()
        return {"success": True, "data": result.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
