import os
import sys

from azure.cognitiveservices.vision.face import FaceClient
from azure.cognitiveservices.vision.face.models import APIErrorException
from msrest.authentication import CognitiveServicesCredentials


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class FaceAPI(metaclass=Singleton):
    def __init__(self):
        self.__face_client = FaceClient(
                os.environ['AZURE_ENDPOINT'],
                CognitiveServicesCredentials(os.environ['AZURE_KEY'])
        )

    def create_person_group(self, id, name):
        self.__face_client.person_group.create(id, name)

    def create_person(self, person_group_id, name, photo_stream, rect):
        rect = [rect.left, rect.top, rect.width, rect.height]
        person = self.__face_client.person_group_person.create(person_group_id, name)
        self.__face_client.person_group_person.add_face_from_stream(person_group_id,
                                                                    person.person_id,
                                                                    photo_stream,
                                                                    target_face=rect)
        return person.person_id

    def train_person_group(self, person_group_id):
        self.__face_client.person_group.train(person_group_id)
        while self.__face_client.person_group.get_training_status(person_group_id).status != 'succeeded':
            if self.__face_client.person_group.get_training_status(person_group_id).status == 'failed':
                print("Training the person group has failed.", file=sys.stderr)
                return

    def identify_faces(self, person_group_id, image_url):
        # Detect faces in the image
        faces = self.__face_client.face.detect_with_stream(open("." + image_url, 'rb'))

        # Identify the faces
        for face in faces:
            try:
                # Identify the face
                possible_persons = self.__face_client.face.identify([face.face_id], person_group_id)
            except APIErrorException as e:
                # Person group training hasn't completed.
                person_id = self.create_person(person_group_id, f"{face.face_id}", open("." + image_url, 'rb'),
                                               face.face_rectangle)
                self.train_person_group(person_group_id)
            else:
                if possible_persons[0].candidates:
                    # Get top matching person
                    person_id = possible_persons[0].candidates[0].person_id
                else:
                    # No one identified
                    person_id = self.create_person(person_group_id, f"{face.face_id}",
                                                   open("." + image_url, 'rb'),
                                                   face.face_rectangle)
                    self.train_person_group(person_group_id)

            yield person_id
