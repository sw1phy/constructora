from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "khuger3894j"

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='constructora',
            ssl_disabled=True
        )
        return conn
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
    
    
@app.route('/')
def home():
    # Redirige a la ruta de registro
    return redirect('/Usuarios/registro')
    
# Ruta para formulario de registro
@app.route('/Usuarios/registro', methods=['GET', 'POST'])
def registro_usuario():
    conn = get_db_connection()
    if not conn:
        return "Error al conectar a la base de datos."

    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = generate_password_hash(request.form['contraseña'])
        rol_id = request.form['rol_id']
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO usuarios (Nombre, Email, Contraseña, Rol_ID) VALUES (%s, %s, %s, %s)", 
                               (nombre, email, contraseña, rol_id))
                conn.commit()
                flash('Usuario registrado exitosamente.', 'success')
                return redirect(url_for('login_usuario'))
        except Error as e:
            print(f"Error al insertar el usuario: {e}")
            flash('Error al registrar usuario.', 'danger')
        finally:
            conn.close()
    
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ID, Rol FROM roles")
            roles = cursor.fetchall()
        return render_template('usuarios/registro.html', roles=roles)
    except Error as e:
        print(f"Error al obtener roles: {e}")
        return "Error al obtener roles."
    finally:
        conn.close()


# Ruta para formulario de login
@app.route('/Usuarios/login', methods=['GET', 'POST'])
def login_usuario():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        conn = get_db_connection()
        if not conn:
            return "Error al conectar a la base de datos."

        try:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT * FROM usuarios WHERE Email = %s", (email,))
                usuario = cursor.fetchone()
                
                if usuario and check_password_hash(usuario['Contraseña'], contraseña):
                    flash('Inicio de sesión exitoso.', 'success')
                    # Aquí podrías redirigir al dashboard u otra vista
                    return redirect(url_for('usuario_index'))
                else:
                    flash('Credenciales incorrectas.', 'danger')
        except Error as e:
            print(f"Error al verificar usuario: {e}")
            flash('Error al iniciar sesión.', 'danger')
        finally:
            conn.close()
    return render_template('usuarios/login.html')


@app.route("/Roles/index")
def rol_index():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Roles")
                datos = cursor.fetchall()
            return render_template('roles/index.html', lista=datos)
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Roles/agregar", methods=["GET"])
def rol_agregar_get():
    return render_template("roles/agregar.html")

@app.route("/Roles/agregar", methods=["POST"])
def rol_agregar_post():
    conn = get_db_connection()
    if conn:
        try:
            v_rol = request.form['rol']
            if v_rol:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO Roles (Rol) VALUES (%s)", (v_rol,))
                    conn.commit()
                return redirect(url_for('rol_index'))
            else:
                return "El rol no puede estar vacío."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Roles/editar/<string:id>", methods=["GET"])
def rol_editar_GET(id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Roles WHERE ID=%s", (id,))
                roll = cursor.fetchone()
            if roll:
                return render_template("roles/editar.html", roll=roll)
            else:
                return "Rol no encontrado."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Roles/editar/<string:id>", methods=["POST"])
def rol_editar_POST(id):
    v_rol = request.form['rol']
    conn = get_db_connection()
    if conn:
        try:
            if v_rol:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE Roles SET Rol=%s WHERE ID=%s", (v_rol, id))
                    conn.commit()
                return redirect(url_for('rol_index'))
            else:
                return "El rol no puede estar vacío."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Roles/eliminar/<string:id>", methods=["POST", "GET"])
def rol_eliminar(id):
    conn = get_db_connection()
    if conn:
        if request.method == 'GET':
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM Roles WHERE ID=%s", (id,))
                    roll = cursor.fetchone()
                if roll:
                    return render_template("roles/eliminar.html", roll=roll)
                else:
                    return "Rol no encontrado."
            except Error as e:
                print(f"Error al ejecutar la consulta: {e}")
                return "Error al ejecutar la consulta."
            finally:
                conn.close()

        if request.method == 'POST':
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM Roles WHERE ID=%s", (id,))
                    conn.commit()
                return redirect(url_for('rol_index'))
            except Error as e:
                print(f"Error al ejecutar la consulta: {e}")
                return "Error al ejecutar la consulta."
            finally:
                conn.close()
    else:
        return "Error al conectar a la base de datos."
    
@app.route("/Usuarios/index")
def usuario_index():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT u.ID, u.Nombre, u.Email, u.Contraseña, r.Rol 
                    FROM Usuarios u
                    JOIN Roles r ON u.Rol_ID = r.ID
                """)
                datos = cursor.fetchall()
            return render_template('usuarios/index.html', lista=datos)
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Usuarios/agregar", methods=["GET"])
def usuario_agregar_get():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Roles")
                roles = cursor.fetchall()

                cursor.execute("SELECT * FROM Usuarios")
                usuarios = cursor.fetchall()

            return render_template("usuarios/agregar.html", roles=roles, usuarios=usuarios)
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Usuarios/agregar", methods=["POST"])
def usuario_agregar_post():
    conn = get_db_connection()
    if conn:
        try:
            v_nombre = request.form['nombre']
            v_email = request.form['email']
            v_contraseña = request.form['contraseña']
            v_rol_id = request.form['rol']
            if v_nombre and v_email and v_contraseña:
                with conn.cursor() as cursor:
                    cursor.execute("INSERT INTO Usuarios (Nombre, Email, Contraseña, Rol_ID) VALUES (%s, %s, %s, %s)",
                                   (v_nombre, v_email, v_contraseña, v_rol_id))
                    conn.commit()
                return redirect(url_for('usuario_index'))
            else:
                return "Todos los campos son requeridos."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Usuarios/editar/<string:id>", methods=["GET"])
def usuario_editar_GET(id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM Roles")
                roles = cursor.fetchall()
                
                cursor.execute("SELECT * FROM Usuarios WHERE ID=%s", (id,))
                usu = cursor.fetchone()
            if usu:
                return render_template("usuarios/editar.html", roles=roles, usu=usu)
            else:
                return "Usuario no encontrado."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Usuarios/editar/<string:id>", methods=["POST"])
def usuario_editar_POST(id):
    
    conn = get_db_connection()
    if conn:
        try:
            v_nombre = request.form['nombre']
            v_email = request.form['email']
            v_contraseña = request.form['contraseña']
            v_rol_id = request.form['rol']
            
            if v_nombre and v_email and v_contraseña:
                with conn.cursor() as cursor:
                    cursor.execute("UPDATE Usuarios SET Nombre=%s, Email=%s, Contraseña=%s, Rol_ID=%s WHERE ID=%s",
                                   (v_nombre, v_email, v_contraseña, v_rol_id, id))
                    conn.commit()
                return redirect(url_for('usuario_index'))
            else:
                return "Todos los campos son requeridos."
        except Error as e:
            print(f"Error al ejecutar la consulta: {e}")
            return "Error al ejecutar la consulta."
        finally:
            conn.close()
    else:
        return "Error al conectar a la base de datos."

@app.route("/Usuarios/eliminar/<string:id>", methods=["POST", "GET"])
def usuario_eliminar(id):
    conn = get_db_connection()
    if conn:
        if request.method == 'GET':
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM Usuarios WHERE ID = %s", (id,))
                    usu = cursor.fetchone()

                    if usu:
                        cursor.execute("SELECT Rol FROM Roles WHERE ID = %s", (usu[4],))
                        rol = cursor.fetchone()

                        if rol:
                            return render_template("usuarios/eliminar.html", usu=usu, rol=rol[0])
                        else:
                            return "Rol no encontrado."
                    else:
                        return "Usuario no encontrado."
            except Error as e:
                print(f"Error al ejecutar la consulta: {e}")
                return "Error al ejecutar la consulta."
            finally:
                conn.close()

        if request.method == 'POST':
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM Usuarios WHERE ID = %s", (id,))
                    conn.commit()
                return redirect(url_for('usuario_index'))
            except Error as e:
                print(f"Error al ejecutar la consulta: {e}")
                return "Error al ejecutar la consulta."
            finally:
                conn.close()
    else:
        return "Error al conectar a la base de datos."

if __name__ == '__main__':
    app.run(debug=True)
