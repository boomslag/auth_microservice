import json, os, django
from confluent_kafka import Consumer
import uuid
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

from django.apps import apps
from apps.user.serializers import UserListSerializer
from core.producer import producer

SellerContact = apps.get_model('contacts', 'SellerContact')
InstructorContact = apps.get_model('contacts', 'InstructorContact')
FriendContact = apps.get_model('contacts', 'FriendContact')
SellerContactList = apps.get_model('contacts', 'SellerContactList')
InstructorContactList = apps.get_model('contacts', 'InstructorContactList')
FriendContactList = apps.get_model('contacts', 'FriendContactList')
Address = apps.get_model('delivery', 'Address')
UserAddresses = apps.get_model('delivery', 'UserAddresses')

class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, uuid.UUID):
            # if obj is uuid, we simply return the value of uuid
            return str(obj)
        return json.JSONEncoder.default(self, obj)

consumer1 = Consumer({
    'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVER'),
    'security.protocol': os.environ.get('KAFKA_SECURITY_PROTOCOL'),
    'sasl.username': os.environ.get('KAFKA_USERNAME'), 
    'sasl.password': os.environ.get('KAFKA_PASSWORD'),
    'sasl.mechanism': 'PLAIN',
    'group.id': os.environ.get('KAFKA_GROUP'),
    'auto.offset.reset': 'earliest'
})
consumer1.subscribe([os.environ.get('KAFKA_TOPIC')])

consumer2 = Consumer({
    'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVER'),
    'security.protocol': os.environ.get('KAFKA_SECURITY_PROTOCOL'),
    'sasl.username': os.environ.get('KAFKA_USERNAME'), 
    'sasl.password': os.environ.get('KAFKA_PASSWORD'),
    'sasl.mechanism': 'PLAIN',
    'group.id': os.environ.get('KAFKA_GROUP_2'),
    'auto.offset.reset': 'earliest'
})
consumer2.subscribe([os.environ.get('KAFKA_TOPIC_2')])

consumer3 = Consumer({
    'bootstrap.servers': os.environ.get('KAFKA_BOOTSTRAP_SERVER'),
    'security.protocol': os.environ.get('KAFKA_SECURITY_PROTOCOL'),
    'sasl.username': os.environ.get('KAFKA_USERNAME'), 
    'sasl.password': os.environ.get('KAFKA_PASSWORD'),
    'sasl.mechanism': 'PLAIN',
    'group.id': os.environ.get('KAFKA_GROUP_3'),
    'auto.offset.reset': 'earliest'
})
consumer3.subscribe([os.environ.get('KAFKA_TOPIC_3')])

while True:
    msg1 = consumer1.poll(1.0)
    msg2 = consumer2.poll(1.0)
    msg3 = consumer3.poll(1.0)

    if msg1 is not None and not msg1.error():
        topic1 = msg1.topic()
        value1 = msg1.value()

        if topic1 == 'users_request':
            if msg1.key() == b'user_id_list':
                # Get user_id list
                user_id_list = User.objects.values_list('id', flat=True)
                # Serialize user_id list
                user_id_list_data = json.dumps(list(user_id_list),cls=UUIDEncoder)
                # producer.produce('users_response', value=user_data)
                producer.produce(
                    'users_response',
                    key='user_id_list',
                    value=user_id_list_data
                )
    
    if msg2 is not None and not msg2.error():
        topic2 = msg2.topic()
        value2 = msg2.value()

        if topic2 == 'user_contacts':
            print(f"Got this message: {msg2}")
            contact_data = json.loads(value2)
            try:
                buyer_id = contact_data['buyer_id']
                seller_id = contact_data['seller_id']
            except KeyError as e:
                print(f"Error in topic '{topic2}' with key '{msg2.key().decode('utf-8')}': Missing field in contact_data: {e}")
                print(f"Full contact_data: {contact_data}")
                continue

            buyer_user = User.objects.get(id=buyer_id)
            seller_user = User.objects.get(id=seller_id)

            if msg2.key() == b'add_instructor_contact':
                print('ADD Instructor to Buyer Contact List')
                contact_list = InstructorContactList.objects.get_or_create(user=buyer_user)[0]
                contact, created = InstructorContact.objects.get_or_create(user=buyer_user, contact=seller_user)

            elif msg2.key() == b'add_seller_contact':
                print('ADD Seller to Buyer Contact List')
                contact_list = SellerContactList.objects.get_or_create(user=buyer_user)[0]
                contact, created = SellerContact.objects.get_or_create(user=buyer_user, contact=seller_user)

            if created:
                print('Contact Added to Buyer Contact List')
                contact_list.contacts.add(contact)
                contact_list.save()

    if msg3 is not None and not msg3.error():
        topic3 = msg3.topic()
        value3 = msg3.value()

        if topic3 == 'delivery_address':
            if msg3.key() == b'store_delivery_address':
                delivery_address_data = json.loads(value3)
                user_id = delivery_address_data['user_id']
                delivery_address = delivery_address_data['delivery_address']

                user = User.objects.get(id=user_id)

                # Create the Address instance
                print("Adding Delivery Address")
                try:
                    new_address = Address.objects.create(
                        user=user,
                        full_name=delivery_address['full_name'],
                        address_line_1=delivery_address['address_line_1'],
                        address_line_2=delivery_address['address_line_2'],
                        city=delivery_address['city'],
                        state_province_region=delivery_address['state_province_region'],
                        postal_zip_code=delivery_address['postal_zip_code'],
                        country_region=delivery_address['country_region'],
                        telephone_number=delivery_address['telephone_number']
                    )
                except:
                    continue

                # Add the Address instance to the UserAddresses
                user_addresses = UserAddresses.objects.get(user=user)
                user_addresses.address.add(new_address)
                user_addresses.save()

consumer1.close()
consumer2.close()
consumer3.close()