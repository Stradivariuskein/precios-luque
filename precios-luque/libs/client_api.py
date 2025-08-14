import dbf

# Ruta a los archivos
clients_files_dbf = ["./siaac_files/siaac3/CLIENTES.DBF", "./siaac_files/siaacfe/CLIENTES.DBF"]


def get_client_from_cuit(cuit):
    # Abre el archivo DBF
    for dbf_file in clients_files_dbf:
        table = dbf.Table(dbf_file)
        table.open()


        # Abrir el archivo DBF con la codificación adecuada
        table = dbf.Table(dbf_file, codepage='cp850')  # Usualmente 'cp850' para MS-DOS
        table.open()


        # search
        for record in table:
            try:
                # Decodificar los valores de texto en caso de que sean bytes
                if isinstance(record.nombre, bytes):
                    record.nombre = record.nombre.decode('cp850', errors='ignore')
                if cuit == record.cuit.replace("-", "").strip():
                    print(f"cuit: {cuit} ")
                    return record
                
            except AttributeError as e:
                print(f"Campo no encontrado en el registro: {e}")
            except UnicodeDecodeError as e:
                print(f"Error de decodificación en el campo 'nombre': {e}")

        # Cierra la tabla
        table.close()
    return None

if __name__ == "__main__":

    print(get_client_from_cuit("11111111115"))

#get_client_from_cuit("27-12412037-9")