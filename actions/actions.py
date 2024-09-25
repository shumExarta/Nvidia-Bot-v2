from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import UserUtteranceReverted
from .functions import (
    get_product,
    get_product_position,
    createJson,
    get_data_from_api,
    get_player_position,
    send_data_to_rag,
    handle_conversation,
    state_maintain,
)
from thefuzz import fuzz, process
import json
import math

# product_list = "./products.json"
state = {}


class ActionMoveTo(Action):
    def name(self) -> Text:
        return "action_move_to"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----MOVE ACTION-----")
        # TRIGGING THE API ENDPOINT TO GET THE DATA HERE
        product_list, product_names, bot_id = get_data_from_api()
        # bot_id = get_bot_id(product_list)
        # player_position = get_player_position()
        # print(f"PLAYER POSITION: {player_position}")
        
        slots = tracker.current_slot_values()
        bot_position = [64.342996, 825.109437, 90.150096]
        product_slot = slots["product"]
        product_slot = process.extractOne(slots['product'], product_names, scorer=fuzz.ratio, score_cutoff=50)

        product = get_product(product_slot[0], product_list)
        product_position = get_product_position(product_slot[0], product_list)

        global state 
        state = state_maintain(
            iD=product['iD'],
            name=product['name'],
            desc=product['desc'],
            price=product['price']
        )
        
        # print(f"STATE : {state}")
        
        message = f"Sure! Let me bring out the {product['name']} for you"

        if math.dist(product_position, bot_position) > 2:
            send_json = createJson(
                iD=product["iD"],
                name=product["name"],
                desc=message,
                translation=product["itemTransform"]["translation"],
                action="PickItem",
                additionalInformation=message,
                bot_id=bot_id
            )

        print(send_json)
        dispatcher.utter_message(message)
        dispatcher.utter_message(json_message=send_json)
        
        player_position = get_player_position()
        print(f"PLAYER POSITION: {player_position}")

        return []


class ActionPlaceItem(Action):
    def name(self) -> Text:
        return "action_place_item"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----PLACE ITEM ACTION-----")
        slots = tracker.current_slot_values()
        
        # TRIGGING THE API ENDPOINT TO GET THE DATA HERE
        product_list, product_names, bot_id = get_data_from_api()
        
        product_slot = process.extractOne(slots['product'], product_names, scorer=fuzz.ratio, score_cutoff=50)
        product = get_product(product_slot[0], product_list)
        print(f"PRODUCT : {product}")
        message = "No worries! Let me know how can I help you better?"
        
        send_json = createJson(
                iD=product["iD"],
                name=product["name"],
                desc=message,
                action="PlaceItem",
                translation=product["itemTransform"]["translation"],
                additionalInformation=message,
                bot_id=bot_id
            )

        dispatcher.utter_message(message)
        dispatcher.utter_message(json_message=send_json)
        return []


class ActionDescribe(Action):
    def name(self) -> Text:
        return "action_describe"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----DESCRIBE PRODUCT ACTION-----")
        global state
        print(f"STATE : {state}")
        # TRIGGING THE API ENDPOINT TO GET THE DATA HERE
        product_list, product_names = get_data_from_api()
        
        slots = tracker.current_slot_values()
        print(f"SLOTS : {slots}")
        
        product_slot = slots["product"]
        product_slot = process.extractOne(slots['product'], product_names, scorer=fuzz.ratio, score_cutoff=50)
        
        product = get_product(product_slot[0], product_list)
        product_position = get_product_position(product_slot[0], product_list)
        
        message = product['desc']
        send_json = createJson(
            iD=product["iD"],
            name=product["name"],
            desc=product["desc"],
            action="Communicate",
            additionalInformation=message
        )
        
        dispatcher.utter_message(message)
        dispatcher.utter_message(json_message=send_json)

        return []


class ActionPickUp(Action):
    def name(self) -> Text:
        return "action_pick_up"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----PICK UP ACTION-----")
        slots = tracker.current_slot_values()
        bot_position = [64.342996, 825.109437, 90.150096]
        product_slot = slots["product"]

        # TRIGGING THE API ENDPOINT TO GET THE DATA HERE
        product_list = get_data_from_api()

        product = get_product(product_slot, product_list)

        try:
            if product:
                product_position = get_product_position(product_slot, product_list)
        except Exception as e:
            print(f"ERROR: {e}")

        if math.dist(product_position, bot_position) > 2:
            send_json = createJson(
                product_id=product["iD"],
                name=product["name"],
                desc=product["desc"],
                translation=product["itemTransform"]["translation"],
                action="PickItem",
            )

        message = f"Sure! Let me bring out the {product['name']} for you."
        dispatcher.utter_message(message)
        dispatcher.utter_message(json.dumps(send_json, indent=4))

        return []


class ActionRag(Action):
    def name(self) -> Text:
        return "action_rag"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----RAG ACTION-----")

        intent = tracker.latest_message['text']
        print(f"INTENT : {intent}")
        rag_response = send_data_to_rag(intent)
        
        send_json = createJson(
            action='Communicate',
            additionalInformation=rag_response
        )
        
        dispatcher.utter_message(rag_response)
        dispatcher.utter_message(json_message=send_json)

        return []


class ActionDefaultFallback(Action):
    def name(self) -> Text:
        return "action_default_fallback"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        print("-----FALLBACK ACTION-----")

        intent = tracker.latest_message['text']
        print(f"INTENT : {intent}")
        
        
        lang_graph_response = handle_conversation(intent)
        
        send_json = createJson(
            action='Communicate',
            additionalInformation=lang_graph_response
        )
        
        dispatcher.utter_message(lang_graph_response)
        dispatcher.utter_message(json_message=send_json)

        return [UserUtteranceReverted()]
