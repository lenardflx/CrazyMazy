# Author: Lenard Felix
 
import os

from dotenv import load_dotenv

load_dotenv()

HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
PORT: int = int(os.getenv("SERVER_PORT", "5555"))
ENV: str = os.getenv("ENV", "dev")
