import unittest
import os
from data_handler import RideDataHandler

class TestRideDataHandler(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_data.json'
        self.handler = RideDataHandler(self.test_file)
        self.handler.usuarios = []
        self.handler.rides = []
        self.handler.participaciones = []
        self.handler.save_data()

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_crear_usuario_exitoso(self):
        data = {"alias": "jperez", "nombre": "Juan Perez", "carPlate": "ABC-123"}
        resultado = self.handler.crear_usuario(data)
        self.assertTrue(resultado)
        self.assertIsNotNone(self.handler.get_usuario("jperez"))

    def test_crear_usuario_duplicado(self):
        data = {"alias": "jperez", "nombre": "Juan Perez"}
        self.handler.crear_usuario(data)
        resultado = self.handler.crear_usuario(data)
        self.assertFalse(resultado)

    def test_get_usuario_no_existente(self):
        self.assertIsNone(self.handler.get_usuario("noexiste"))

    def test_crear_ride_exitoso(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan Perez"})
        ride = {
            'id': 1,
            'rideDateAndTime': '2025-07-16 12:00',
            'finalAddress': 'Av Siempre Viva 123',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 2,
            'participants': []
        }
        self.handler.rides.append(ride)
        self.handler.save_data()
        self.assertEqual(len(self.handler.rides), 1)

    def test_request_to_join_ride_no_existe(self):
        resultado = self.handler.request_to_join(1, 'lgomez', {
            'destination': 'Av Aramburú 245',
            'occupiedSpaces': 1
        })
        self.assertEqual(resultado, 'Ride no encontrado')

    def test_request_to_join_ya_solicito(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        ride = {
            'id': 1,
            'rideDateAndTime': '2025-08-01 10:00',
            'finalAddress': 'Centro',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 2,
            'participants': []
        }
        self.handler.rides.append(ride)
        self.handler.request_to_join(1, 'ana', {'destination': 'Centro', 'occupiedSpaces': 1})
        res = self.handler.request_to_join(1, 'ana', {'destination': 'Centro', 'occupiedSpaces': 1})
        self.assertEqual(res, 'Ya solicitó unirse')

    def test_aceptar_participante_sin_asientos(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        ride = {
            'id': 1,
            'rideDateAndTime': '2025-08-01 10:00',
            'finalAddress': 'Centro',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 1,
            'participants': []
        }
        self.handler.rides.append(ride)
        self.handler.request_to_join(1, 'ana', {'destination': 'Centro', 'occupiedSpaces': 2})
        res = self.handler.aceptar_participante(1, 'ana')
        self.assertEqual(res, 'No hay asientos disponibles')

    def test_aceptar_participante_ya_confirmado(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        ride = {
            'id': 2,
            'rideDateAndTime': '2025-08-01 11:00',
            'finalAddress': 'Centro',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 2,
            'participants': [{
                'participant': 'ana',
                'destination': 'Centro',
                'occupiedSpaces': 1,
                'status': 'waiting',
                'confirmation': 'confirmed'
            }]
        }
        self.handler.rides.append(ride)
        res = self.handler.aceptar_participante(2, 'ana')
        self.assertEqual(res, 'Ya fue aceptado o rechazado')

    def test_rechazar_participante_no_existe(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        ride = {
            'id': 3,
            'rideDateAndTime': '2025-08-01 12:00',
            'finalAddress': 'Centro',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 2,
            'participants': []
        }
        self.handler.rides.append(ride)
        res = self.handler.rechazar_participante(3, 'ana')
        self.assertEqual(res, 'Participante no encontrado')

    def test_iniciar_y_terminar_ride(self):
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        ride = {
            'id': 4,
            'rideDateAndTime': '2025-08-02 10:00',
            'finalAddress': 'Centro',
            'driver': 'jperez',
            'status': 'ready',
            'availableSeats': 2,
            'participants': [{
                'participant': 'ana',
                'destination': 'Centro',
                'occupiedSpaces': 1,
                'status': 'waiting',
                'confirmation': 'confirmed'
            }]
        }
        self.handler.rides.append(ride)
        r = self.handler.iniciar_ride(4, ['ana'])
        self.assertEqual(r, 'ok')
        self.assertEqual(ride['participants'][0]['status'], 'inprogress')
        t = self.handler.terminar_ride(4)
        self.assertEqual(t, 'ok')
        self.assertEqual(ride['participants'][0]['status'], 'notmarked')

    def test_bajar_participante(self):
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        ride = {
            'id': 5,
            'rideDateAndTime': '2025-08-03 08:00',
            'finalAddress': 'Parque',
            'driver': 'jperez',
            'status': 'inprogress',
            'availableSeats': 2,
            'participants': [{
                'participant': 'ana',
                'destination': 'Parque',
                'occupiedSpaces': 1,
                'status': 'inprogress',
                'confirmation': 'confirmed'
            }]
        }
        self.handler.rides.append(ride)
        res = self.handler.bajar_participante(5, 'ana')
        self.assertEqual(res, 'ok')
        self.assertEqual(ride['participants'][0]['status'], 'completed')

    def test_get_rides_por_usuario(self):
        self.handler.crear_usuario({"alias": "luis", "nombre": "Luis"})
        self.handler.rides.append({"id": 1, "driver": "luis", "status": "ready", "participants": []})
        self.handler.rides.append({"id": 2, "driver": "ana", "status": "ready", "participants": []})
        rides = self.handler.get_rides_por_usuario("luis")
        self.assertEqual(len(rides), 1)
        self.assertEqual(rides[0]['driver'], 'luis')

    def test_get_participantes_estadisticas(self):
        self.handler.crear_usuario({"alias": "ana", "nombre": "Ana"})
        self.handler.rides.append({
            'id': 6,
            'driver': 'jperez',
            'status': 'done',
            'availableSeats': 2,
            'participants': [
                {'participant': 'ana', 'status': 'completed', 'occupiedSpaces': 1, 'destination': 'A', 'confirmation': 'confirmed'},
                {'participant': 'ana', 'status': 'missing', 'occupiedSpaces': 1, 'destination': 'B', 'confirmation': 'confirmed'},
                {'participant': 'ana', 'status': 'notmarked', 'occupiedSpaces': 1, 'destination': 'C', 'confirmation': 'confirmed'},
                {'participant': 'ana', 'status': 'rejected', 'occupiedSpaces': 1, 'destination': 'D', 'confirmation': 'rejected'}
            ]
        })
        participantes = self.handler.get_participantes_estadisticas(6)
        self.assertEqual(participantes[0]['participant']['previousRidesCompleted'], 1)
        self.assertEqual(participantes[0]['participant']['previousRidesMissing'], 1)
        self.assertEqual(participantes[0]['participant']['previousRidesNotMarked'], 1)
        self.assertEqual(participantes[0]['participant']['previousRidesRejected'], 1)

    def test_crear_usuarioD(self):
        resultado = self.handler.crear_usuarioD({"alias": "ana", "nombre": "Ana"})
        self.assertTrue(resultado)

if __name__ == '__main__':
    unittest.main()
