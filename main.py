from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from pymongo import MongoClient, errors
from bson.objectid import ObjectId
from kivy.uix.spinner import Spinner
from pymongo.errors import OperationFailure


# Configuration of connection MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["students"]
collection = db["data_students"]

class CRUDApp(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"

        # Enter Data
            # ID (search and delete)
        self.add_widget(Label(text="ID"))
        self.id_input = TextInput(multiline=False, disabled=True)
        self.id_input.bind(text=self.id_text_change)
        self.add_widget(self.id_input)

            # Control number
        self.add_widget(Label(text="Número de Control"))
        self.numControl_input = TextInput(multiline=False)
        self.numControl_input.bind(text=self.data_text_change)
        self.add_widget(self.numControl_input)

            # Name
        self.add_widget(Label(text="Nombre"))
        self.name_input = TextInput(multiline=False)
        self.name_input.bind(text=self.data_text_change)
        self.add_widget(self.name_input)

            # Career spinner
        self.add_widget(Label(text="Carrera"))
        self.career_spinner = self.create_career_spinner()
        self.career_spinner.bind(text=self.data_text_change)
        self.add_widget(self.career_spinner)

            # Address
        self.add_widget(Label(text="Dirección"))
        self.address_input = TextInput(multiline=False)
        self.address_input.bind(text=self.data_text_change)
        self.add_widget(self.address_input)

            # Email
        self.add_widget(Label(text="E-mail"))
        self.email_input = TextInput(multiline=False)
        self.email_input.bind(text=self.data_text_change)
        self.add_widget(self.email_input)

            # Phone
        self.add_widget(Label(text="Teléfono"))
        self.phone_input = TextInput(multiline=False)
        self.phone_input.bind(text=self.data_text_change)
        self.add_widget(self.phone_input)
        
        # Buttons to operations CRUD
        self.add_button = Button(text="Agregar", disabled=True)
        self.add_button.bind(on_press=self.create)
        self.add_widget(self.add_button)

        self.search_button = Button(text="Buscar")
        self.search_button.bind(on_press=self.show_search_popup)
        self.add_widget(self.search_button)

        self.update_button = Button(text="Actualizar", disabled=True)
        self.update_button.bind(on_press=self.update)
        self.add_widget(self.update_button)

        self.delete_button = Button(text="Eliminar", disabled=True)
        self.delete_button.bind(on_press=self.show_delete_popup)
        self.add_widget(self.delete_button)

    def create_career_spinner(self):
        # Career spinner contains the careers can be add to the data base
        careers_array = [
            'Ingeniería Bioquímica', 'Ingeniería Civil', 'Ingeniería Electromecánica', 'Ingeniería en Sistemas Computacionales',
            'Ingeniería en TICs', 'Ingeniería Industrial'
        ]
        career_spinner = Spinner(
            text='Seleccionar carrera...',  # Initial text
            values=careers_array,            # Menu options
            size_hint=(1, None),             # Automatic width relative at window
            height=44                         # Fixed height
        )
        return career_spinner

    def id_text_change(self, instance, value):
        # States of update and delete buttons, disabled if id is empty
        self.update_button.disabled = not value.strip()
        self.delete_button.disabled = not value.strip()

    def data_text_change(self, instance, value):
        # State of add button
        if (self.numControl_input.text.strip() and
            self.name_input.text.strip() and
            self.career_spinner.text != 'Seleccionar carrera...' and
            self.address_input.text.strip() and
            self.email_input.text.strip() and
            self.phone_input.text.strip() and
            not self.id_input.text.strip()
            ):
            self.add_button.disabled = False  # Enable if all fields have text
            self.search_button.disabled = True
        else:
            self.add_button.disabled = True   # Disable if any field is empty
            self.search_button.disabled = False

    def show_error_popup(self, message):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        
        # Label with the message
        layout.add_widget(Label(text=message))
        
        # OK button to close the popup
        close_button = Button(text="OK", size_hint=(1, 0.3))
        layout.add_widget(close_button)
        
        # Create the popup and add the layout with the button and the message
        popup = Popup(
            title="Error",
            content=layout,
            size_hint=(0.6, 0.4),
        )
        
        # Function to close the popup when clicking OK
        close_button.bind(on_release=popup.dismiss)

        popup.open()

    def show_successful_popup(self, message):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)
        
        # Label with the message
        layout.add_widget(Label(text=message))
        
        # OK button to close the popup
        close_button = Button(text="OK", size_hint=(1, 0.3))
        layout.add_widget(close_button)
        
        # Create the popup and add the layout with the button and the message
        popup = Popup(
            title="Tarea exitosa",
            content=layout,
            size_hint=(0.6, 0.4),
        )
        
        # Function to close the popup when clicking OK
        close_button.bind(on_release=popup.dismiss)
        
        popup.open()

    def validate_empty_inputs(self):
        # Validate that no field is empty
        if (not self.numControl_input.text 
            or not self.name_input.text 
            or self.career_spinner.text == 'Seleccionar carrera...'
            or not self.address_input.text
            or not self.email_input.text
            or not self.phone_input.text
            ):
            self.show_error_popup("Todos los campos deben ser llenados")
            return False
        return True

    def handle_operation_error(self, e):
        # Errors of operations with MongoDB
        # Verify if code error is 121 (validation error)
        if isinstance(e, OperationFailure) and e.code == 121:
            # Simplify error details
            error_details = e.details['errInfo']['details']['schemaRulesNotSatisfied'][0]['propertiesNotSatisfied']
            
            # Dictionary of type 'switch' that associated DB variables with specific messages
            error_popup_messages = {
                'num_control': "Número de control inválido\n\nRecuerda que debe ser de 8 dígitos",
                'career': "Debes escoger una carrera",
                'email': "Correo electrónico inválido\n\nRecuerda que el dominio debe ser @itsm.edu.mx",
                'phone': "Número de teléfono inválido\n\nRecuerda que debe contener solo números y ser de 10 dígitos",
            }
            
            for detail in error_details:
                property_name = detail['propertyName']
                reason = detail['details'][0]['reason']
                value = detail['details'][0].get('consideredValue', 'Valor no disponible')
                
                # Verify if property is on the errors dictionary
                if property_name in error_popup_messages:
                    custom_message = error_popup_messages[property_name]

                    # Show PopUp with message personalized
                    #self.show_error_popup(f"{custom_message} Detalle: {reason}. Valor ingresado: {value}")
                    self.show_error_popup(f"{custom_message}")
                else:
                    # If not in the dictionary, show the general error
                    print(f"Error en '{property_name}': {reason}. Valor ingresado: {value}")
        else:
            # Show other errors of operation
            print(f"Error de operación: {e}")

    def create(self, instance):
        # Validate data before create
        if not self.validate_empty_inputs():
            return

        # Insert new document
        data = {
            "num_control": self.numControl_input.text,
            "name": self.name_input.text,
            "career": self.career_spinner.text,
            "address": self.address_input.text,
            "email": self.email_input.text,
            "phone": self.phone_input.text
        }

        try:
            collection.insert_one(data)
            self.show_successful_popup("Registro agregado")
            self.clear_inputs()
        except errors.DuplicateKeyError:
            self.show_error_popup("El número de control ingresado ya existe en la base de datos.")
        except Exception as e:
            self.handle_operation_error(e)

    def show_search_popup(self, instance):
        # Popup to enter ID
        self.popup_layout = BoxLayout(orientation="vertical")
        self.popup_layout.add_widget(Label(text="Ingrese el ID"))
        
        self.popup_id_input = TextInput(multiline=False)
        self.popup_layout.add_widget(self.popup_id_input)
        
        search_button = Button(text="Buscar")
        search_button.bind(on_press=self.search)
        self.popup_layout.add_widget(search_button)
        
        self.search_popup = Popup(title="Buscar alumno", content=self.popup_layout, size_hint=(0.8, 0.5))
        self.search_popup.open()

    def search(self, instance):
        # Search ID
        try:
            document_id = ObjectId(self.popup_id_input.text)
        except:
            if not self.popup_id_input.text:
                self.show_error_popup("Campo vacío, ingrese un ID.")
            else:
                self.show_error_popup("El ID proporcionado no es válido.")
            return

        result = collection.find_one({"_id": document_id})
        if result:
            self.id_input.text = str(result["_id"])
            self.numControl_input.text = result["num_control"]
            self.name_input.text = result["name"]
            self.career_spinner.text = result["career"]
            self.address_input.text = result["address"]
            self.email_input.text = result["email"]
            self.phone_input.text = result["phone"]

            self.search_popup.dismiss()
        else:
            self.show_error_popup("Registro no encontrado.")

    def update(self, instance):
        # Validate data before update
        if not self.validate_empty_inputs():
            return

        new_data = {
            "num_control": self.numControl_input.text,
            "name": self.name_input.text,
            "career": self.career_spinner.text,
            "address": self.address_input.text,
            "email": self.email_input.text,
            "phone": self.phone_input.text
        }

        try:
            collection.update_one({"_id": ObjectId(self.id_input.text)}, {"$set": new_data})
            self.show_successful_popup("Registro actualizado.")
            self.clear_inputs()
        except Exception as e:
            self.handle_operation_error(e)

    def show_delete_popup(self, instance):        
        # Show popup of confirm
        confirm_layout = BoxLayout(orientation="vertical")
        confirm_layout.add_widget(Label(text="¿Está seguro de que desea eliminar este registro?"))
        
        yes_button = Button(text="Sí")
        yes_button.bind(on_press=self.delete)
        confirm_layout.add_widget(yes_button)

        no_button = Button(text="No")
        no_button.bind(on_press=self.close_delete_popup)
        confirm_layout.add_widget(no_button)

        self.delete_popup = Popup(title="Eliminar Registro", content=confirm_layout, size_hint=(0.8, 0.5))
        self.delete_popup.open()

    def close_delete_popup(self, instance):
        # Close popup
        self.delete_popup.dismiss()

    def delete(self, instance):
        # Delete register|student
        try:
            collection.delete_one({"_id": ObjectId(self.id_input.text)})
            self.show_successful_popup("Registro eliminado.")
            self.clear_inputs()
        except:
            self.show_error_popup("Error al intentar borrar el registro.")
            return
        self.delete_popup.dismiss()

    def clear_inputs(self):
        # Clear all fields
        self.id_input.text = ""
        self.numControl_input.text = ""
        self.name_input.text = ""
        self.career_spinner.text = "Seleccionar carrera..."
        self.address_input.text = ""
        self.email_input.text = ""
        self.phone_input.text = ""

        if hasattr(self, 'popup_id_input'):
            self.popup_id_input.text = ""


class MainApp(App):
    def build(self):
        return CRUDApp()


if __name__ == "__main__":
    MainApp().run()
