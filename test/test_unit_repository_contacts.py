import unittest
import first_task.routes.contacts
from first_task.models import contact

class TestRepositoryContacts(unittest.TestCase):
    def test_get_contact_by_id(self):
        fake_db = [contact(id=1, name="Test", email="test@mail.com", phone="123")]
        result = first_task.routes.contacts.get_contact_by_id(1, db=fake_db)
        self.assertIsNotNone(result)
        self.assertEqual(result.id, 1)

if __name__ == '__main__':
    unittest.main()
