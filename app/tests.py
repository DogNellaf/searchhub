from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import Client, TestCase

from app.models import Query, Result, Summary
from app.utils import (
    count_keywords,
    generate_summary,
    get_search_results,
    search_duckduckgo,
    search_google,
)


# ---------------------------------------------------------------------------
# Utility function tests
# ---------------------------------------------------------------------------

class CountKeywordsTest(TestCase):
    def test_empty_text_returns_zero(self):
        self.assertEqual(count_keywords('', ['python']), 0)

    def test_empty_keywords_returns_zero(self):
        self.assertEqual(count_keywords('python django', []), 0)

    def test_single_keyword_counted(self):
        self.assertEqual(count_keywords('python is great and python rocks', ['python']), 2)

    def test_case_insensitive(self):
        self.assertEqual(count_keywords('Python DJANGO python', ['python']), 2)

    def test_multiple_keywords(self):
        self.assertEqual(count_keywords('python django web python', ['python', 'django']), 3)

    def test_no_match_returns_zero(self):
        self.assertEqual(count_keywords('hello world', ['python']), 0)


class SearchGoogleTest(TestCase):
    @patch('app.utils.requests.get')
    def test_returns_items_on_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            'items': [{'title': 'Test', 'link': 'http://test.com', 'snippet': 'Test snippet'}]
        }
        mock_get.return_value.raise_for_status = lambda: None
        result = search_google('test query')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['title'], 'Test')

    @patch('app.utils.requests.get')
    def test_returns_empty_when_no_items(self, mock_get):
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.raise_for_status = lambda: None
        self.assertEqual(search_google('test query'), [])

    @patch('app.utils.requests.get')
    def test_returns_empty_on_exception(self, mock_get):
        mock_get.side_effect = Exception('Connection error')
        self.assertEqual(search_google('test query'), [])

    @patch('app.utils.requests.get')
    def test_url_encodes_query(self, mock_get):
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.raise_for_status = lambda: None
        search_google('hello world')
        called_url = mock_get.call_args[0][0]
        self.assertIn('hello+world', called_url)


class SearchDuckDuckGoTest(TestCase):
    @patch('app.utils.requests.get')
    def test_returns_topics_on_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            'RelatedTopics': [{'Text': 'Topic', 'FirstURL': 'http://test.com'}]
        }
        mock_get.return_value.raise_for_status = lambda: None
        result = search_duckduckgo('test query')
        self.assertEqual(len(result), 1)

    @patch('app.utils.requests.get')
    def test_returns_empty_when_no_topics(self, mock_get):
        mock_get.return_value.json.return_value = {}
        mock_get.return_value.raise_for_status = lambda: None
        self.assertEqual(search_duckduckgo('test query'), [])

    @patch('app.utils.requests.get')
    def test_returns_empty_on_exception(self, mock_get):
        mock_get.side_effect = Exception('Connection error')
        self.assertEqual(search_duckduckgo('test query'), [])


class GetSearchResultsTest(TestCase):
    @patch('app.utils.search_duckduckgo')
    @patch('app.utils.search_google')
    def test_combines_both_engines(self, mock_google, mock_ddg):
        mock_google.return_value = [
            {'title': 'G1', 'link': 'http://g1.com', 'snippet': 'Google result'}
        ]
        mock_ddg.return_value = [
            {'Text': 'D1', 'FirstURL': 'http://d1.com'}
        ]
        results = get_search_results('test')
        self.assertEqual(len(results), 2)

    @patch('app.utils.search_duckduckgo')
    @patch('app.utils.search_google')
    def test_returns_empty_when_all_fail(self, mock_google, mock_ddg):
        mock_google.return_value = []
        mock_ddg.return_value = []
        self.assertEqual(get_search_results('test'), [])

    @patch('app.utils.search_duckduckgo')
    @patch('app.utils.search_google')
    def test_duckduckgo_items_without_url_skipped(self, mock_google, mock_ddg):
        mock_google.return_value = []
        mock_ddg.return_value = [{'Text': 'No URL item'}]
        self.assertEqual(get_search_results('test'), [])


class GenerateSummaryTest(TestCase):
    def test_returns_fallback_for_empty_results(self):
        result = generate_summary([])
        self.assertIn('отсутств', result.lower())

    def test_returns_fallback_for_empty_snippets(self):
        result = generate_summary([{'snippet': ''}, {'snippet': '   '}])
        self.assertIn('отсутств', result.lower())

    @patch('app.utils.OpenAI')
    def test_returns_summary_on_success(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.return_value.choices[0].message.content = '  Test summary  '
        result = generate_summary([{'snippet': 'Some text to summarize'}])
        self.assertEqual(result, 'Test summary')

    @patch('app.utils.OpenAI')
    def test_returns_fallback_on_api_error(self, mock_openai_class):
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception('API error')
        result = generate_summary([{'snippet': 'Some text'}])
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)


# ---------------------------------------------------------------------------
# View tests
# ---------------------------------------------------------------------------

class SignupViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_get_returns_form(self):
        response = self.client.get('/signup/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_authenticated_user_redirects_to_search(self):
        User.objects.create_user('auth_user', password='pass123')
        self.client.login(username='auth_user', password='pass123')
        response = self.client.get('/signup/')
        self.assertRedirects(response, '/')

    def test_post_creates_user_and_redirects(self):
        response = self.client.post('/signup/', {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'SecurePass123',
            'password2': 'SecurePass123',
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertRedirects(response, '/')

    def test_post_duplicate_username_shows_error(self):
        User.objects.create_user('existinguser', password='pass123')
        response = self.client.post('/signup/', {
            'username': 'existinguser',
            'email': 'e@example.com',
            'password': 'SecurePass123',
            'password2': 'SecurePass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_post_password_mismatch_shows_form(self):
        response = self.client.post('/signup/', {
            'username': 'user1',
            'email': 'u@example.com',
            'password': 'pass123',
            'password2': 'different',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')

    def test_post_empty_username_shows_form(self):
        response = self.client.post('/signup/', {
            'username': '',
            'password': 'pass123',
            'password2': 'pass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'signup.html')


class LoginViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', password='testpass123')

    def test_get_returns_form(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_authenticated_user_redirects_to_search(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get('/login/')
        self.assertRedirects(response, '/')

    def test_post_valid_credentials_redirects_to_search(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'testpass123',
        })
        self.assertRedirects(response, '/')

    def test_post_invalid_credentials_shows_form(self):
        response = self.client.post('/login/', {
            'username': 'testuser',
            'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_post_nonexistent_user_shows_form(self):
        response = self.client.post('/login/', {
            'username': 'nobody',
            'password': 'pass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_next_parameter_redirects_after_login(self):
        response = self.client.post('/login/?next=/history/', {
            'username': 'testuser',
            'password': 'testpass123',
            'next': '/history/',
        })
        self.assertRedirects(response, '/history/')


class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('logoutuser', password='pass123')

    def test_logout_redirects_to_login(self):
        self.client.login(username='logoutuser', password='pass123')
        response = self.client.post('/logout/')
        self.assertRedirects(response, '/login/')

    def test_logout_clears_session(self):
        self.client.login(username='logoutuser', password='pass123')
        self.client.post('/logout/')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)


class SearchViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('searchuser', password='pass123')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_get_shows_search_form(self):
        self.client.login(username='searchuser', password='pass123')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')

    @patch('app.views.get_search_results')
    @patch('app.views.generate_summary')
    def test_post_runs_search_and_shows_results(self, mock_summary, mock_search):
        self.client.login(username='searchuser', password='pass123')
        mock_search.return_value = [
            {'title': 'Result 1', 'url': 'http://r1.com', 'snippet': 'Snippet 1'}
        ]
        mock_summary.return_value = 'Test summary'

        response = self.client.post('/', {'text': 'test query'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results.html')

    @patch('app.views.get_search_results')
    @patch('app.views.generate_summary')
    def test_post_saves_query_to_database(self, mock_summary, mock_search):
        self.client.login(username='searchuser', password='pass123')
        mock_search.return_value = []
        mock_summary.return_value = 'Результаты отсутствуют'

        self.client.post('/', {'text': 'django test'})
        self.assertTrue(Query.objects.filter(text='django test', user=self.user).exists())

    @patch('app.views.get_search_results')
    @patch('app.views.generate_summary')
    def test_post_saves_results_to_database(self, mock_summary, mock_search):
        self.client.login(username='searchuser', password='pass123')
        mock_search.return_value = [
            {'title': 'R1', 'url': 'http://r1.com', 'snippet': 'S1'},
            {'title': 'R2', 'url': 'http://r2.com', 'snippet': 'S2'},
        ]
        mock_summary.return_value = 'summary'

        self.client.post('/', {'text': 'query'})
        query = Query.objects.get(text='query', user=self.user)
        self.assertEqual(query.results.count(), 2)

    def test_post_empty_query_stays_on_search_page(self):
        self.client.login(username='searchuser', password='pass123')
        response = self.client.post('/', {'text': '   '})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertEqual(Query.objects.filter(user=self.user).count(), 0)

    @patch('app.views.get_search_results')
    @patch('app.views.generate_summary')
    def test_results_sorted_by_keyword_relevance(self, mock_summary, mock_search):
        self.client.login(username='searchuser', password='pass123')
        mock_search.return_value = [
            {'title': 'Low', 'url': 'http://low.com', 'snippet': 'generic text'},
            {'title': 'High', 'url': 'http://high.com', 'snippet': 'python python python'},
        ]
        mock_summary.return_value = 'summary'

        response = self.client.post('/', {'text': 'python'})
        results = response.context['results']
        self.assertEqual(results[0]['title'], 'High')


class HistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('histuser', password='pass123')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.get('/history/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)

    def test_authenticated_shows_history(self):
        self.client.login(username='histuser', password='pass123')
        Query.objects.create(user=self.user, text='test query')
        response = self.client.get('/history/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'history.html')
        self.assertContains(response, 'test query')

    def test_only_shows_own_history(self):
        other = User.objects.create_user('other', password='pass123')
        Query.objects.create(user=other, text='other query')
        self.client.login(username='histuser', password='pass123')
        response = self.client.get('/history/')
        self.assertNotContains(response, 'other query')

    def test_pagination_10_items_per_page(self):
        self.client.login(username='histuser', password='pass123')
        for i in range(15):
            Query.objects.create(user=self.user, text=f'query {i}')
        response = self.client.get('/history/')
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_page_two_shows_remaining_items(self):
        self.client.login(username='histuser', password='pass123')
        for i in range(15):
            Query.objects.create(user=self.user, text=f'query {i}')
        response = self.client.get('/history/?page=2')
        self.assertEqual(len(response.context['page_obj']), 5)


class DeleteHistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('deluser', password='pass123')
        self.query = Query.objects.create(user=self.user, text='to delete')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.post(f'/history/delete/{self.query.id}/')
        self.assertIn('/login/', response.url)

    def test_delete_own_history_item(self):
        self.client.login(username='deluser', password='pass123')
        response = self.client.post(f'/history/delete/{self.query.id}/')
        self.assertFalse(Query.objects.filter(id=self.query.id).exists())
        self.assertRedirects(response, '/history/')

    def test_cannot_delete_another_users_item(self):
        other = User.objects.create_user('other2', password='pass123')
        other_query = Query.objects.create(user=other, text='others query')
        self.client.login(username='deluser', password='pass123')
        self.client.post(f'/history/delete/{other_query.id}/')
        self.assertTrue(Query.objects.filter(id=other_query.id).exists())

    def test_get_request_redirects_without_deleting(self):
        self.client.login(username='deluser', password='pass123')
        self.client.get(f'/history/delete/{self.query.id}/')
        self.assertTrue(Query.objects.filter(id=self.query.id).exists())


class ClearHistoryViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('clearuser', password='pass123')
        Query.objects.create(user=self.user, text='query 1')
        Query.objects.create(user=self.user, text='query 2')

    def test_unauthenticated_redirects_to_login(self):
        response = self.client.post('/history/clear/')
        self.assertIn('/login/', response.url)

    def test_clears_all_own_history(self):
        self.client.login(username='clearuser', password='pass123')
        response = self.client.post('/history/clear/')
        self.assertEqual(Query.objects.filter(user=self.user).count(), 0)
        self.assertRedirects(response, '/history/')

    def test_does_not_affect_other_users_history(self):
        other = User.objects.create_user('other3', password='pass123')
        Query.objects.create(user=other, text='other query')
        self.client.login(username='clearuser', password='pass123')
        self.client.post('/history/clear/')
        self.assertEqual(Query.objects.filter(user=other).count(), 1)

    def test_get_request_redirects_without_clearing(self):
        self.client.login(username='clearuser', password='pass123')
        self.client.get('/history/clear/')
        self.assertEqual(Query.objects.filter(user=self.user).count(), 2)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

class QueryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('modeluser', password='pass123')

    def test_str_returns_query_text(self):
        query = Query.objects.create(user=self.user, text='test query')
        self.assertEqual(str(query), 'test query')

    def test_timestamp_set_automatically(self):
        query = Query.objects.create(user=self.user, text='test')
        self.assertIsNotNone(query.timestamp)

    def test_default_ordering_newest_first(self):
        q1 = Query.objects.create(user=self.user, text='first')
        q2 = Query.objects.create(user=self.user, text='second')
        queries = list(Query.objects.filter(user=self.user))
        self.assertEqual(queries[0], q2)
        self.assertEqual(queries[1], q1)

    def test_cascade_delete_removes_results(self):
        query = Query.objects.create(user=self.user, text='test')
        Result.objects.create(query=query, title='R', url='http://r.com', description='d')
        query.delete()
        self.assertEqual(Result.objects.count(), 0)

    def test_cascade_delete_removes_summaries(self):
        query = Query.objects.create(user=self.user, text='test')
        Summary.objects.create(query=query, text='summary')
        query.delete()
        self.assertEqual(Summary.objects.count(), 0)


class ResultModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('resultuser', password='pass123')
        self.query = Query.objects.create(user=self.user, text='test')

    def test_str_returns_title(self):
        result = Result.objects.create(
            query=self.query,
            title='Test Result',
            url='http://example.com',
            description='A test result',
        )
        self.assertEqual(str(result), 'Test Result')

    def test_related_name_access(self):
        Result.objects.create(query=self.query, title='R', url='http://r.com', description='d')
        self.assertEqual(self.query.results.count(), 1)


class SummaryModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('summaryuser', password='pass123')
        self.query = Query.objects.create(user=self.user, text='test')

    def test_str_returns_first_50_chars(self):
        long_text = 'A' * 100
        summary = Summary.objects.create(query=self.query, text=long_text)
        self.assertEqual(str(summary), 'A' * 50)

    def test_related_name_access(self):
        Summary.objects.create(query=self.query, text='summary text')
        self.assertEqual(self.query.summaries.count(), 1)
