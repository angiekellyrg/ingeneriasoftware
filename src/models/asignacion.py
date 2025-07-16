class Asignacion:
    def __init__(self, task_id, user_id):
        self.task_id = task_id
        self.user_id = user_id

    def get_assignment_details(self):
        return {
            "task_id": self.task_id,
            "user_id": self.user_id
        }