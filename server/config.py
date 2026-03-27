# Author: Lenard Felix
 
import os

HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
PORT: int = int(os.getenv("PORT", "5555"))
ENV: str = os.getenv("ENV", "dev")