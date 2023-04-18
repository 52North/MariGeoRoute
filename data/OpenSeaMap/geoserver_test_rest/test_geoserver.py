import zipfile
import requests
import psycopg2
import os
from dotenv import load_dotenv


# loading all the necessary environment variables
#requires .env file
load_dotenv()


class CONNECTDB:
    """
    Initialize connection variables, connect to the postgis database and get the filtered list of tables.
    """

    def __init__(self):

        # GeoServer REST API endpoint
        self.geoserver_url = 'http://localhost/geoserver'
        self.geoserver_url_rest = 'http://localhost/geoserver/rest/'

        # GeoServer credentials
        self.geo_username = 'admin'
        self.geo_password = 'geoserver'

        # PostgreSQL connection details
        self.database = 'geoserver'
        self.user = 'geonode'
        self.password = 'geonode'
        self.host = 'localhost'
        self.port = '5432'

    def connectDB_getTables(self):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(database=self.database, user=self.user,
                                password=self.password, host=self.host, port=self.port)
        self.cur = conn.cursor()

        # Get the list of tables in the public schema
        self.cur.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE'")
        tables = self.cur.fetchall()
        # print(tables)

        filtered_tables = [table[0] for table in tables if table[0].endswith(
            ('_point', '_line', '_polygon', '_roads'))]

        return filtered_tables


class GEOREST:
    """
    Initialize workspace and datastore , get or create the workspace , get or create the datastore and save the layers to the geoserver
    """

    def __init__(self, workspace_name, datastore_name):
        self.db_api = CONNECTDB()
        self.workspace_name = workspace_name
        self.datastore_name = datastore_name

    def get_or_create_workspace(self):
        """
        Checks if a workspace exists in GeoServer and returns its name if it does,
        or creates a new workspace and returns its name if it does not.
        """
        # Retrieve the list of workspaces
        workspaces_url = f"{self.db_api.geoserver_url}/rest/workspaces.json"
        workspaces_data = requests.get(workspaces_url, auth=(
            self.db_api.geo_username, self.db_api.geo_password)).json()
        workspaces = [workspace["name"]
                      for workspace in workspaces_data["workspaces"]["workspace"]]

        # Check if the workspace already exists
        if self.workspace_name in workspaces:
            print(f"Workspace '{self.workspace_name}' already exists.")
        else:
            # Define the JSON payload for creating the new workspace
            new_workspace_json = {
                "workspace": {
                    "name": self.workspace_name
                }
            }
            # Create the new workspace
            requests.post(f"{self.db_api.geoserver_url}/rest/workspaces.json",
                          json=new_workspace_json, auth=(self.db_api.geo_username, self.db_api.geo_password))
            print(f"Workspace '{self.workspace_name}' created.")

        return self.workspace_name

    def get_or_create_datastore(self):
        """
        Checks if a datastore exists in the specified workspace in GeoServer and
        returns its name if it does, or creates a new datastore with the specified
        name and returns its name if it does not.
        """
        # Retrieve the list of datastores for the specified workspace
        datastores_url = f"{self.db_api.geoserver_url}/rest/workspaces/{self.workspace_name}/datastores.json"
        datastores_data = requests.get(datastores_url, auth=(
            self.db_api.geo_username, self.db_api.geo_password)).json()

        # Check if the datastores list is empty
        if "dataStores" not in datastores_data or "dataStore" not in datastores_data["dataStores"]:
            datastores = []
        else:
            datastores = [datastore["name"]
                          for datastore in datastores_data["dataStores"]["dataStore"]]

        # Check if the datastore already exists
        if self.datastore_name in datastores:
            print(
                f"Datastore '{self.datastore_name}' already exists in workspace '{self.workspace_name}'.")
        else:
            # Define the JSON payload for creating the new datastore

            new_datastore_json = {
                "dataStore": {
                    "name": self.datastore_name,
                    "connectionParameters": {
                        "entry": [
                            {"@key": "host",
                                "$": os.environ.get('POSTGIS_HOST_DB')},
                            {"@key": "port",
                                "$": os.environ.get("POSTGIS_PORT")},
                            {"@key": "database",
                                "$": os.environ.get("POSTGIS_DATABASE")},
                            {"@key": "user",
                                "$": os.environ.get("POSTGIS_USER")},
                            {"@key": "passwd",
                                "$": os.environ.get("POSTGIS_PASSWORD")},
                            {"@key": "dbtype", "$": "postgis"},
                            {"@key": "schema", "$": "public"},
                            {"@key": "validate connections", "$": "true"},
                            {"@key": "max connections", "$": "10"},
                        ]
                    }
                }
            }
            print(new_datastore_json)

            requests.post(f"{self.db_api.geoserver_url}/rest/workspaces/{self.workspace_name}/datastores.json",
                          json=new_datastore_json, auth=(self.db_api.geo_username, self.db_api.geo_password))
            print(
                f"Datastore '{self.datastore_name}' created in workspace '{self.workspace_name}'.")

        return self.datastore_name

    def create_layers_postgis2geoserver(self, table_names):
        for table_name in table_names:
            # Define the JSON payload for creating the new layer
            new_layer_json = {
                "featureType": {
                    "name": table_name,
                    "nativeName": table_name,
                    "title": table_name,
                    "abstract": table_name,
                    "nativeCRS": "EPSG:4326",
                    "enabled": True,
                    "store": {
                        "@class": "dataStore",
                        "name": self.datastore_name,
                        "href": f"{self.db_api.geoserver_url}/rest/workspaces/{self.workspace_name}/datastores/{self.datastore_name}.json"
                    }
                }
            }
            # Create the new layer
            requests.post(f"{self.db_api.geoserver_url}/rest/workspaces/{self.workspace_name}/datastores/{self.datastore_name}/featuretypes.json",
                          json=new_layer_json, auth=(self.db_api.geo_username, self.db_api.geo_password))
            print(
                f"Layer '{table_name}' created in datastore '{self.datastore_name}' in workspace '{self.workspace_name}'.")

    def create_layers_from_shapefile(self, file):

        workspace_url = self.db_api.geoserver_url_rest + \
            'workspaces/' + self.workspace_name

        response = requests.get(workspace_url, auth=(
            self.db_api.geo_username, self.db_api.geo_password))

        if response.status_code == 404:
            headers = {'Content-type': 'application/xml'}
            data = '<workspace><name>{0}</name></workspace>'.format(
                self.workspace_name)
            response = requests.post(workspace_url, headers=headers, data=data, auth=(
                self.db_api.geo_username, self.db_api.geo_password))
            if response.status_code != 201:
                print(
                    f"Error creating workspace: {response.status_code} {response.text}")
                return

        headers = {'Content-type': 'application/zip'}
        shapefile_name = 'seamarks_multilinestrings'

        with open(file, 'rb') as f:
            response = requests.put(
                self.db_api.geoserver_url_rest +
                'workspaces/{0}/datastores/{1}/file.shp'.format(
                    self.workspace_name, self.datastore_name),
                headers=headers,
                data=f,
                auth=(self.db_api.geo_username, self.db_api.geo_password)
            )
            if response.status_code != 201:
                print(
                    f"Error uploading shapefile: {response.status_code} {response.text}")
                return

        headers = {'Content-type': 'application/xml'}

        data = '''
        <featureType>
        <name>{0}</name>
        <nativeName>{1}</nativeName>
        <title>{0}</title>
        <srs>EPSG:4326</srs>
        </featureType>
        '''.format(shapefile_name, shapefile_name)

        response = requests.post(
            self.db_api.geoserver_url_rest +
            'workspaces/{0}/datastores/{1}/featuretypes'.format(
                self.workspace_name, shapefile_name),
            headers=headers,
            data=data,
            auth=(self.db_api.geo_username, self.db_api.geo_password)
        )
        if response.status_code != 201:
            print(
                f"Error creating layer: {response.status_code} {response.text}")
        else:
            print('Layer saved successfully')

    def create_layer_shp(self,shapefile_directory,shapefile):
        geoserver_url = self.db_api.geoserver_url
        username = 'admin'
        password = 'geoserver'

        # Set path to the shapefile directory
        shapefile_dir = shapefile_directory 

        # Set workspace name and store name for the new shapefile
        workspace = self.get_or_create_workspace()
        store_name = self.get_or_create_datastore()

        # Set the name of the shapefile
        shapefile_name = shapefile 

        # Set the path to the shapefile zip file
        shapefile_zip_path = os.path.join(
            shapefile_dir, shapefile_name + '.zip')

        # Check if zip file exists, otherwise include all files with shapefile_name into the zip
        if not os.path.exists(shapefile_zip_path):
            with zipfile.ZipFile(shapefile_zip_path, mode='w', compression=zipfile.ZIP_DEFLATED) as zipf:
                for file in os.listdir(shapefile_dir):
                    if file.startswith(shapefile_name):
                        zipf.write(os.path.join(shapefile_dir, file), file)

        # Upload the shapefile to GeoServer
        headers = {'Content-type': 'application/zip'}
        auth = (username, password)
        upload_url = f"{geoserver_url}/rest/workspaces/{workspace}/datastores/{store_name}/file.shp"
        with open(shapefile_zip_path, 'rb') as f:
            response = requests.put(
                upload_url, headers=headers, data=f, auth=auth)
        print(response.status_code)

        # Publish the shapefile as a layer
        publish_url = f"{geoserver_url}/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes"
        xml = f"""
            <featureType>
                <name>{shapefile_name}</name>
                <nativeName>{shapefile_name}</nativeName>
            </featureType>
        """
        headers = {'Content-type': 'application/xml'}
        response = requests.post(
            publish_url, headers=headers, data=xml, auth=auth)
        print(response.status_code)

    def create_layer_shp_unzip(self):
        geoserver_url = self.db_api.geoserver_url
        username = 'admin'
        password = 'geoserver'

        # Set path to the shapefile directory
        shapefile_dir = 'D:/shp'

        # Set workspace name and store name for the new shapefile
        workspace = self.workspace_name
        store_name = self.datastore_name

        # Set the name of the shapefile
        shapefile_name = 'seamarks_multilinestrings'

        # Set the path to the shapefile files
        shapefile_path = os.path.join(shapefile_dir, shapefile_name)

        # Upload the shapefile to GeoServer
        headers = {'Content-type': 'application/zip'}
        auth = (username, password)
        upload_url = f"{geoserver_url}/rest/workspaces/{workspace}/datastores/{store_name}/file.shp"
        with open(shapefile_path + '.shp', 'rb') as shp_file, \
                open(shapefile_path + '.shx', 'rb') as shx_file, \
                open(shapefile_path + '.dbf', 'rb') as dbf_file:
            files = {'file': (shapefile_name + '.shp', shp_file),
                     'file': (shapefile_name + '.shx', shx_file),
                     'file': (shapefile_name + '.dbf', dbf_file)}
            response = requests.put(upload_url, files=files, auth=auth)
        print(response.status_code)

        # Publish the shapefile as a layer
        publish_url = f"{geoserver_url}/rest/workspaces/{workspace}/datastores/{store_name}/featuretypes"
        xml = f"""
            <featureType>
                <name>{shapefile_name}</name>
                <nativeName>{shapefile_name}</nativeName>
            </featureType>
        """
        headers = {'Content-type': 'application/xml'}
        response = requests.post(
            publish_url, headers=headers, data=xml, auth=auth)
        print(response.status_code)


if __name__ == "__main__":
    # This code only runs when the module is executed as the main program
    rest = GEOREST('geonode', 'geoserver')
    # rest.get_or_create_datastore()
    # rest.get_or_create_workspace()
    # rest.create_layers(rest.db_api.connectDB_getTables())
    # rest.create_layers_from_shapefile('D:/shp/seamarks_multilinestrings.shp')
    rest.create_layer_shp('C:/Users/Surendra/Downloads/coastlines-split','lines')
