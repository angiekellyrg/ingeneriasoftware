class Tarea:
    def __init__(self, id, title, description, status='pending'):
        self.id = id
        self.title = title
        self.description = description
        self.status = status

    def mark_complete(self):
        self.status = 'completed'