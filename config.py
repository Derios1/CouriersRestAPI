username = "derios"
password = "Sekret_45"
host = "localhost"
port = "5432"
database = "shop"
database_url = "postgresql://{}:{}@{}:{}/{}".format(username,
                                                    password,
                                                    host, port,
                                                    database)
