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
        """✅ Crear un usuario nuevo correctamente"""
        data = {"alias": "jperez", "nombre": "Juan Perez", "carPlate": "ABC-123"}
        resultado = self.handler.crear_usuario(data)
        self.assertTrue(resultado)
        self.assertIsNotNone(self.handler.get_usuario("jperez"))

    def test_crear_usuario_duplicado(self):
        """❌ No se puede crear un usuario con alias duplicado"""
        data = {"alias": "jperez", "nombre": "Juan Perez"}
        self.handler.crear_usuario(data)
        resultado = self.handler.crear_usuario(data)
        self.assertFalse(resultado)

    def test_get_usuario_no_existente(self):
        """❌ Buscar un usuario que no existe debe devolver None"""
        self.assertIsNone(self.handler.get_usuario("noexiste"))

    def test_crear_ride_exitoso(self):
        """✅ Crear un ride correctamente para un usuario existente"""
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
        """❌ Error: Ride no encontrado al solicitar unirse"""
        resultado = self.handler.request_to_join(1, 'lgomez', {
            'destination': 'Av Aramburú 245',
            'occupiedSpaces': 1
        })
        self.assertEqual(resultado, 'Ride no encontrado')

    def test_request_to_join_ya_solicito(self):
        """❌ Ya solicitó unirse al ride"""
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
        """❌ No hay asientos disponibles al aceptar participante"""
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
        """❌ Ya fue aceptado o rechazado"""
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
        """❌ Participante no encontrado en ride"""
        self.handler.crear_usuario({"alias": "jperez", "nombre": "Juan"})
        ride = {
            'id': 3,