import traceback
import requests
import json

class Mail_activations():
    def __init__(self, token = None):
        if token != None:
            self.token = token
        else:
            raise Token_is_empty

    def balance(self, api = 2.0):
        url = "http://api.kopeechka.store/user-balance"
        query = {"token":self.token, "api" : api}
        responce = requests.get(url=url, params=query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_get_email(self, site = None, mail_type = None, sender = None, regex = None, soft_id = None, investor = None, subject = None, clear = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-get-email"
        query = {"site" : site, "mail_type" : mail_type, "sender" : sender, "regex" : regex, "token" : self.token, "soft" : soft_id, "investor" : investor, "subject" : subject, "clear" : clear, "api" : api}
        responce = requests.get(url=url, params=query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_get_message(self, full = None, task_id = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-get-message"
        query = {"full" : full, "id" : task_id, "token" : self.token, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_cancel(self, task_id = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-cancel"
        query = {"id" : task_id, "token" : self.token, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_reorder(self, site=None, email = None, regex = None, subject=None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-reorder"
        query = {"site" : site, "email" : email, "regex" : regex, "token" : self.token, "subject" : subject, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_get_fresh_id(self, site=None, email=None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-get-fresh-id"
        query = {"token" : self.token, "site" : site, "email" : email, "api" : api}
        responce = requests.get(url=url, params=query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_set_comment(self, task_id = None, comment = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-set-comment"
        query = {"token" : self.token, "id" : task_id, "comment" : comment, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_get_bulk(self, count = None, text = None, email = None, site = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-get-bulk"
        query = {"token" : self.token, "count" : count, "comment" : text, "email" : email, "site" : site, "api":api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def domain_add_blacklist(self, domain = None, site = None, expire = None, api = 2.0):
        url = "http://api.kopeechka.store/domain-add-blacklist"
        query = {"token" : self.token, "domain" : domain, "site" : site, "expire" : expire, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def domain_exclude_blacklist(self, domain = None, site = None, api = 2.0):
        url = "http://api.kopeechka.store/domain-exclude-blacklist"
        query = {"token" : self.token, "domain" : domain, "site" : site, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def blacklist_get_service(self, site=None, api = 2.0):
        url = "http://api.kopeechka.store/blacklist-get-service"
        query = {"token" : self.token, "site" : site, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_get_domains(self, site = None, api = 2.0):
        url = "http://api.kopeechka.store/mailbox-get-domains"
        query = {"token" : self.token, "site" : site, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def mailbox_zones(self, popular = None, zones = None):
        url = "https://api.kopeechka.store/mailbox-zones"
        query = {"popular":popular, "zones" : zones}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer

    def domain_get_alive(self, domain = None, api = 2.0):
        url = "http://api.kopeechka.store/domain-get-alive"
        query = {"domain" : domain, "api" : api}
        responce = requests.get(url, query)
        answer = responce.text
        if answer == "":
            return {"status":"ERROR", "value":"SYSTEM_ERROR"}
        answer = json.loads(answer)
        return answer