import os
import requests
import logging

logger = logging.getLogger(__name__)

class APIClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(APIClient, cls).__new__(cls)
            cls._instance.base_url = os.getenv("API_BASE_URL", "http://localhost:8080/api")
            cls._instance.token = None
        return cls._instance

    def set_token(self, token):
        self.token = token

    def clear_token(self):
        self.token = None

    def _get_headers(self):
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def register(self, username, password, email=None):
        url = f"{self.base_url}/auth/register"
        payload = {"username": username, "password": password}
        if email:
            payload["email"] = email
        try:
            response = requests.post(url, json=payload, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API register error: {e}")
            return {"detail": "Server connection failed"}, 503

    def login(self, username, password):
        url = f"{self.base_url}/auth/login"
        # OAuth2 password flow expects form data
        data = {"username": username, "password": password}
        try:
            response = requests.post(url, data=data, timeout=5)
            res_data = response.json()
            if response.status_code == 200:
                self.token = res_data.get("access_token")
            return res_data, response.status_code
        except Exception as e:
            logger.error(f"API login error: {e}")
            return {"detail": "Server connection failed"}, 503

    def get_profile(self):
        url = f"{self.base_url}/auth/me"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API get profile error: {e}")
            return {"detail": "Server connection failed"}, 503

    def search_flights(self, origin=None, destination=None, date=None):
        url = f"{self.base_url}/flights/search"
        params = {}
        if origin:
            params["origin"] = origin
        if destination:
            params["destination"] = destination
        if date:
            params["date"] = date
        try:
            response = requests.get(url, params=params, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API search flights error: {e}")
            return [], 503

    def get_flight_details(self, flight_id):
        url = f"{self.base_url}/flights/{flight_id}"
        try:
            response = requests.get(url, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API get flight error: {e}")
            return {"detail": "Server connection failed"}, 503

    def book_flight(self, flight_id, passenger_name, passport_number):
        url = f"{self.base_url}/bookings/book"
        payload = {
            "flight_id": flight_id,
            "passenger_name": passenger_name,
            "passport_number": passport_number
        }
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API book flight error: {e}")
            return {"detail": "Server connection failed"}, 503

    def cancel_booking(self, booking_id):
        url = f"{self.base_url}/bookings/{booking_id}/cancel"
        try:
            response = requests.post(url, headers=self._get_headers(), timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API cancel booking error: {e}")
            return {"detail": "Server connection failed"}, 503

    def get_my_orders(self):
        url = f"{self.base_url}/bookings/my-orders"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API get orders error: {e}")
            return [], 503

    def get_statistics(self):
        url = f"{self.base_url}/bookings/statistics"
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API get statistics error: {e}")
            return {"avg_prices": [], "booking_volume": []}, 503

    def ask_ai(self, query):
        url = f"{self.base_url}/ai/ask"
        payload = {"query": query}
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=20) # AI might take longer
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API ask AI error: {e}")
            return {"response": "AI Advisor Server is offline or timed out.", "context": [], "mode": "Error"}, 503

    def get_weather(self, destination):
        url = f"{self.base_url}/external/weather"
        params = {"destination": destination}
        try:
            response = requests.get(url, params=params, timeout=5)
            return response.json(), response.status_code
        except Exception as e:
            logger.error(f"API weather error: {e}")
            return {"detail": "Weather service unavailable"}, 503

# Global singleton client
api_client = APIClient()
