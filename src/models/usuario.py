class Usuario:
    def __init__(self, user_id, name, email):
        self.id = user_id
        self.name = name
        self.email = email

    def get_user_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }