import json

class RideDataHandler:
    def __init__(self, filename='data.json'):
        self.filename = filename
        self.usuarios = []
        self.rides = []
        self.participaciones = []  # Para estadísticas si se quiere guardar
        self.load_data()

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump({
                'usuarios': self.usuarios,
                'rides': self.rides,
                'participaciones': self.participaciones
            }, f, indent=4)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                data = json.load(f)
                self.usuarios = data.get('usuarios', [])
                self.rides = data.get('rides', [])
                self.participaciones = data.get('participaciones', [])
        except FileNotFoundError:
            self.usuarios = []
            self.rides = []
            self.participaciones = []

    def get_usuario(self, alias):
        return next((u for u in self.usuarios if u['alias'] == alias), None)

    def crear_usuarioD(self, data):
        if self.get_usuario(data['alias']):
            return False
        nuevo_usuario = {
            "alias": data["alias"],
            "nombre": data["nombre"],
            "carPlate": data.get("carPlate"),
            "rides": []
        }
        self.usuarios.append(nuevo_usuario)
        self.save_data()
        return True
    
    def crear_usuario(self, data):
        if self.get_usuario(data['alias']):
            return False
        nuevo_usuario = {
            "alias": data["alias"],
            "nombre": data["nombre"],
            "carPlate": data.get("carPlate"),
            "rides": []
        }
        self.usuarios.append(nuevo_usuario)
        self.save_data()
        return True

    def get_ride(self, id):
        return next((r for r in self.rides if r['id'] == id), None)

    def get_rides_por_usuario(self, alias):
        return [r for r in self.rides if r['driver'] == alias]

    def request_to_join(self, rideid, alias, data):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        if ride['status'] != 'ready':
            return 'Ride ya ha iniciado'
        if any(p['participant'] == alias for p in ride['participants']):
            return 'Ya solicitó unirse'
        ride['participants'].append({
            'participant': alias,
            'destination': data['destination'],
            'occupiedSpaces': data['occupiedSpaces'],
            'status': 'waiting',
            'confirmation': None
        })
        self.save_data()
        return 'ok'

    def aceptar_participante(self, rideid, alias):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        participante = next((p for p in ride['participants'] if p['participant'] == alias), None)
        if not participante:
            return 'Participante no encontrado'
        if participante['confirmation'] is not None:
            return 'Ya fue aceptado o rechazado'
        total_ocupado = sum(p['occupiedSpaces'] for p in ride['participants'] if p['confirmation'] == 'confirmed')
        if total_ocupado + participante['occupiedSpaces'] > ride['availableSeats']:
            return 'No hay asientos disponibles'
        participante['confirmation'] = 'confirmed'
        participante['status'] = 'waiting'
        self.save_data()
        return 'ok'

    def rechazar_participante(self, rideid, alias):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        participante = next((p for p in ride['participants'] if p['participant'] == alias), None)
        if not participante:
            return 'Participante no encontrado'
        participante['confirmation'] = 'rejected'
        participante['status'] = 'rejected'
        self.save_data()
        return 'ok'

    def iniciar_ride(self, rideid, presentes):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        for p in ride['participants']:
            if p['confirmation'] == 'confirmed':
                if p['participant'] in presentes:
                    p['status'] = 'inprogress'
                else:
                    p['status'] = 'missing'
        ride['status'] = 'inprogress'
        self.save_data()
        return 'ok'

    def terminar_ride(self, rideid):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        for p in ride['participants']:
            if p['status'] == 'inprogress':
                p['status'] = 'notmarked'
        ride['status'] = 'done'
        self.save_data()
        return 'ok'

    def bajar_participante(self, rideid, alias):
        ride = self.get_ride(rideid)
        if not ride:
            return 'Ride no encontrado'
        p = next((p for p in ride['participants'] if p['participant'] == alias), None)
        if not p or p['status'] != 'inprogress':
            return 'No estás en viaje'
        p['status'] = 'completed'
        self.save_data()
        return 'ok'

    def get_participantes_estadisticas(self, rideid):
        ride = self.get_ride(rideid)
        if not ride:
            return []
        participantes_info = []
        for p in ride.get('participants', []):
            alias = p['participant']
            estadisticas = self.get_estadisticas(alias)
            participantes_info.append({
                'confirmation': p['confirmation'],
                'participant': {
                    'alias': alias,
                    **estadisticas
                },
                'destination': p['destination'],
                'occupiedSpaces': p['occupiedSpaces'],
                'status': p['status']
            })
        return participantes_info

    def get_estadisticas(self, alias):
        total = 0
        completed = 0
        missing = 0
        notmarked = 0
        rejected = 0

        for ride in self.rides:
            for p in ride.get("participants", []):
                if p["participant"] == alias:
                    total += 1
                    status = p["status"]
                    if status == "completed":
                        completed += 1
                    elif status == "missing":
                        missing += 1
                    elif status == "notmarked":
                        notmarked += 1
                    elif status == "rejected":
                        rejected += 1

        return {
            "previousRidesTotal": total,
            "previousRidesCompleted": completed,
            "previousRidesMissing": missing,
            "previousRidesNotMarked": notmarked,
            "previousRidesRejected": rejected
        }
