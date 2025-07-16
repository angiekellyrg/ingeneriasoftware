from flask import Flask, jsonify, request
from data_handler import RideDataHandler

app = Flask(__name__)
data_handler = RideDataHandler()

@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    return jsonify(data_handler.usuarios)

@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    if not data_handler.crear_usuario(data):
        return jsonify({'error': 'Usuario ya existe'}), 422
    return jsonify({'message': 'Usuario creado'}), 201

@app.route('/usuarios/<alias>', methods=['GET'])
def obtener_usuario(alias):
    user = data_handler.get_usuario(alias)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    return jsonify(user)
@app.route('/rides', methods=['POST'])
def crear_ride():
    data = request.json
    driver = data.get('driver')
    user = data_handler.get_usuario(driver)
    if not user:
        return jsonify({'error': 'Usuario no encontrado'}), 404

    new_ride = {
        'id': len(data_handler.rides) + 1,
        'rideDateAndTime': data.get('rideDateAndTime'),
        'finalAddress': data.get('finalAddress'),
        'driver': driver,
        'status': 'ready',
        'availableSeats': data.get('availableSeats'),
        'participants': []
    }
    data_handler.rides.append(new_ride)
    data_handler.save_data()
    return jsonify({'rideId': new_ride['id']}), 201

@app.route('/usuarios/<alias>/rides', methods=['GET'])
def rides_usuario(alias):
    if not data_handler.get_usuario(alias):
        return jsonify({'error': 'Usuario no encontrado'}), 404
    rides = data_handler.get_rides_por_usuario(alias)
    return jsonify(rides)

@app.route('/usuarios/<alias>/rides/<int:rideid>', methods=['GET'])
def detalle_ride(alias, rideid):
    ride = data_handler.get_ride(rideid)
    if not ride or ride['driver'] != alias:
        return jsonify({'error': 'Ride no encontrado'}), 404
    participantes = data_handler.get_participantes_estadisticas(rideid)
    ride['participants'] = participantes
    return jsonify({'ride': ride})

@app.route('/usuarios/<alias>/rides/<int:rideid>/requestToJoin/<participant_alias>', methods=['POST'])
def request_join(alias, rideid, participant_alias):
    result = data_handler.request_to_join(rideid, participant_alias, request.json)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Solicitud enviada'})

@app.route('/usuarios/<alias>/rides/<int:rideid>/accept/<participant_alias>', methods=['POST'])
def aceptar_participante(alias, rideid, participant_alias):
    result = data_handler.aceptar_participante(rideid, participant_alias)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Participante aceptado'})

@app.route('/usuarios/<alias>/rides/<int:rideid>/reject/<participant_alias>', methods=['POST'])
def rechazar_participante(alias, rideid, participant_alias):
    result = data_handler.rechazar_participante(rideid, participant_alias)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Participante rechazado'})

@app.route('/usuarios/<alias>/rides/<int:rideid>/start', methods=['POST'])
def iniciar_ride(alias, rideid):
    presentes = request.json.get('presentes', [])
    result = data_handler.iniciar_ride(rideid, presentes)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Ride iniciado'})

@app.route('/usuarios/<alias>/rides/<int:rideid>/end', methods=['POST'])
def terminar_ride(alias, rideid):
    result = data_handler.terminar_ride(rideid)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Ride terminado'})

@app.route('/usuarios/<alias>/rides/<int:rideid>/unloadParticipant', methods=['POST'])
def bajar_participante(alias, rideid):
    result = data_handler.bajar_participante(rideid, alias)
    if result != 'ok':
        return jsonify({'error': result}), 422
    return jsonify({'message': 'Participante bajó del ride'})

if __name__ == '__main__':
    app.run(debug=True)
