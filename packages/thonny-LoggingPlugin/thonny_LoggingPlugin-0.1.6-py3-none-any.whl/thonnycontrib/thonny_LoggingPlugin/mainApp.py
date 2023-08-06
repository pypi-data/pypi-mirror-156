from thonny import get_workbench
from thonny.shell import ShellView

import tkinter as tk
import logging
from datetime import datetime
from copy import deepcopy
import os

import thonnycontrib.thonny_LoggingPlugin.utils.logger_utils as lutils
from thonnycontrib.thonny_LoggingPlugin.processing import formatData
from thonnycontrib.thonny_LoggingPlugin.configuration import configuration
from thonnycontrib.thonny_LoggingPlugin.configuration.globals import *
from thonnycontrib.thonny_LoggingPlugin.communication.sendingClient import SendingClient

SERVER_ADDR = "127.0.0.0"
SENDING = False
LOG_IN_CONSOLE = False
FOLDER = DEFAULT_PATH

class EventLogger:
    """
    Main class to generate logs from user's actions
    This class

    Attributes :
        events (:obj:'list'): Store the logs in order to write them in a file
        _sending_logs (bool): True for write the logs in a file, false if not
        _textInsertBuffer (:obj:'dict') Temporary store a TextInsert dict
        _inDict  (:obj:'dict') Store the templates of inputs logs we want
        _textInsertBuffer (:obj)
    """

    def __init__(self):
        """
        Construct an instance of EventLogger, initiates the attributes and makes the binds to get our data
        """
        # Stockage dans la ram des logs pour les enregistrer dans un fichier lors de la fermeture de thonny
        self.events = []
        self.formatted_logs = []

        # Instance de la classe de formatage
        self.export_formater = formatData.FormatData(self)
        # Instance de la classe d'envoi des données au serveur
        self.sending_client = SendingClient(SERVER_ADDR)

        #Variable qui défini si l'utilisateur veut ou non l'enregistrement des traces
        self._sending_logs = SENDING
        self.log_in_console = LOG_IN_CONSOLE

        #Pour _Buffer_Text
        self._textInsertBuffer = dict()
        self._stderrBuffer = dict()
        #Stockage des codeStates selon l'id de l'événement qui les a enregistré
        self._codeStates = dict()


        #Attribut des éléments que l'on veut séléctionner :
        self._inDict = {
            "ShellCommand" : {'sequence','command_text','tags'},
            "ShellInput" : {'sequence','input_text','tags'},
            "TextInsert" : {'sequence','index','text','text_widget','text_widget_context','tags'},
            "TextDelete" : {'sequence','index1','index2','text','text_widget','text_widget_context','tags'},

            "Save" : {'sequence','editor','text_widget','filename'},
            "NewFile" : {'sequence','editor','text_widget','filename'},
            "Open" : {'sequence','editor','text_widget','filename'},
            "SaveAs" : {'sequence','editor','text_widget','filename'},

            "l1Tests" : {'sequence','filename','tested_line','expected_result','obtained_result'}
        }

        for sequence in self._inDict:
            self._bind(sequence)
        self._bind("UiCommandDispatched")

        get_workbench().bind("WorkbenchClose", self._on_workbench_close, True)

        #Lance le début de Session du formater ici pour éviter problème de chargement de fichier avant début de session
        self.export_formater.begin_session(id(self))

    def _on_workbench_close(self, event):
        """
        write logs and codeState in files in directory specified in the config
        """
        self.export_formater.end_session(id(event))
        if self._sending_logs :
            try : 
                os.mkdir(FOLDER+"/logs")
            except FileExistsError as e :
                pass
            try : 
                os.mkdir(FOLDER+"/codeStates")
            except FileExistsError :
                pass

            import json
            #Base logs
            with open(FOLDER+'/logs/logs.json', encoding="UTF-8", mode="w") as fp:
                json.dump(self.events, fp, indent="    ")
            #Pre formatted logs
            with open(FOLDER+'/logs/formatted_logs.json', encoding="UTF-8", mode="w") as fp:
                json.dump(self.formatted_logs,fp,indent="    ")
            #CodeStates
            #with open(FOLDER+'/codeStates/codeStates.txt', encoding="UTF-8", mode="w") as fp:
            #    fp.write(json.dumps(self._codeStates))

    def _bind(self,sequence):
        """
        bind an event 'sequence' to produce logs

        Args: 
            sequence (str): the event name

        Returns:
            None
        """
        def handle(event):
            self._prepare_log(sequence,event)
        
        get_workbench().bind(sequence,handle,True)


    def _prepare_log(self,sequence,event):
        """
        Triggered by the event, make logs and write them in console and store them in an attribute

        Args:
            sequence (str): the event name
            event (:object:)
        """
        data = self._extract_interesting_data(event, sequence)

        data["time"] = datetime.now().isoformat()

        data = self._input_processing(data,event)

        self._log_event(data,event)


    def _log_event(self,data,event):
        """
        print logs in console and store them in an attribute

        Args:
            data (obj:'dict'): the data in the format we want
        """
        if data != {}:
            self.events.append(data)
            #standard print in shell
            if self.log_in_console :
                print(data)
            self.export_formater.init_event(data,id(event))

    def _extract_interesting_data(self, event, sequence):
        """
        Extract data from an event and select only the informations we need

        Returns:
            (obj:'dict'): the data in the format we want
        """
        attributes = vars(event)
        data = {'tags': () }


        if "text_widget" not in attributes:
            if "editor" in attributes:
                attributes["text_widget"] = attributes["editor"].get_text_widget()

            if "widget" in attributes and isinstance(attributes["widget"], tk.Text):
                attributes["text_widget"] = attributes["widget"]


        if "text_widget" in attributes:
            widget = attributes["text_widget"]
            if isinstance(widget.master.master, ShellView):
                attributes["text_widget_context"] = "shell"


        for elem in self._inDict[sequence]:
            if elem in attributes:
                value = attributes[elem]
                data[elem] = value
                if isinstance(value, (tk.BaseWidget, tk.Tk)):
                    data[elem + "_id"] = id(value)
                    data[elem + "_class"] = value.__class__.__name__

        return data

    def _input_processing(self,data,event):
        """
        Process the data to obtain something more interesting to exploit

        Args :
            data (object:'dict') Data to process

        Returns :
            data (object:'dict') Data modified
        """
        # Partie nettoyage
        if 'editor' in data :
            del data['editor']
            del data['editor_class']

        
        #Pas utilisé pour l'instant
        if data['sequence'] in {"Save","NewFile","Open","SaveAs"} :
            # key : event id
            # value : (widget id, content)
            self._codeStates[id(event)] = (id(data['text_widget']),data['text_widget'].get('1.0', 'end'))

        if data['sequence'] == 'ShellCommand' :
            data['editorContent'] = get_workbench().get_editor_notebook().get_current_editor_content()

        #Maintenant on ne s'en sert plus
        if 'text_widget' in data :
            del data['text_widget']

        # Partie traitement et filtrage
        if data['sequence'] == 'TextInsert' :
            if 'text_widget' in data :
                del data['text_widget']
            if data["text_widget_class"] == 'ShellText':
                if not 'value' in data['tags'] and not 'stderr' in data['tags'] and not 'stdout' in data['tags']:
                    if 'prompt' in data['tags']:
                        data = deepcopy(self._stderrBuffer)
                        self._stderrBuffer = {}
                        self._log_event(data,event)
                        self.export_formater.end_event()
                    return {}
                else :
                    if 'stderr' in data['tags']:
                        self._buffer_text(data)
                        return {}

            # EditorCodeViewText et CodeViewText désignent la même chose mais le premier dans la version 4.0.0 de thonny et le second dans la version 3.3.14
            elif data['text_widget_class'] == 'EditorCodeViewText' or data['text_widget_class'] == 'CodeViewText':
                return self._buffer_text(data)
             
        elif data['sequence'] == 'TextDelete' :
            return {}


        return data
       

    def _buffer_text(self,data):
        """
        Store in a buffer the data of user's text edition events and return when the user
        write somewhere else

        Args : 
            data (object:'dict'): Data to process

        Returns :
            (object:'dict'): an empty dict if the user keep writing of the same line,
            the data stored in buffer else.

        """
        if data['text_widget_class'] == 'EditorCodeViewText' or data['text_widget_class'] == 'CodeViewText' :
            buf = deepcopy(self._textInsertBuffer)

            if buf == {}:
                self._textInsertBuffer = data
                return {}

            else :
                if data['text'] == '\n':
                    buf['text'] += '\n'
                    self._textInsertBuffer = {}
                    return buf

                if not lutils.indexs_on_same_line(data['index'],buf['index']) : 
                    self._textInsertBuffer = data
                    return buf
                
                else :

                    x1 = lutils.getX(buf['index'])
                    x2 = lutils.getX(data['index'])

                    # Si la lettre est insérée à la suite :
                    if x2 == (x1 + len(buf['text'])):
                        self._textInsertBuffer['text'] = buf['text'] + data['text']
                        return {}
                    
                    else :
                        x = x2 - x1
                        self._textInsertBuffer['text'] = buf['text'][:x] + data['text'] + buf['text'][x:]
                        return {}

        else :
            if 'stderr' in data['tags']:
                buf = deepcopy(self._stderrBuffer)
                if buf == {}:
                    self._stderrBuffer = data
                else :
                    self._stderrBuffer['text'] = buf['text']+data['text']
                
        return {}

    def receive_formatted_logs(self,formatted_log):
        """
        Store and send the formatted logs in parameter to a Server if the user didn't desactivate it
        Args :
            formatted_log (object:'dict') the logs in a basic exportation format
        """
        #Pour l'instant, on stocke aussi une trace localement:
        self.formatted_logs.append(formatted_log)
        print(formatted_log)
        try :
            if self._sending_logs :
                self.sending_client.send_statement(formatted_log)

        except KeyError as e :
            logging.info(formatted_log,e)
            return 