import logging

from tracker.core.connectors.webhook_parser import WebHookDataParser, ParseError, RefChangeRequest

logger = logging.getLogger("webhook-parser")


class GithubHookParser(WebHookDataParser):

    def parse(self, request) -> RefChangeRequest:
        if len(request["commits"]) == 0:
            logger.info("Nothing was changed")
            raise ParseError()

        link = request["repository"]["clone_url"]
        to_hash = request["after"]
        from_hash = request["before"]
        repo_name = request["repository"]["name"]
        if request['created']:
            type = 'CREATE'
        elif request['deleted']:
            type = 'DELETE'
        else:
            type = 'UPDATE'
        ref_id = request["ref"].replace("refs/heads", "refs/remotes/origin")

        logger.info("Parsed request: {} {} {} {} {} {}".format(repo_name, link, type, to_hash, from_hash, ref_id))
        ref_request = RefChangeRequest(
            repo_name=repo_name,
            repo_link=link,
            update_type=type,
            to_hash=to_hash,
            from_hash=from_hash,
            ref_id=ref_id
        )
        return ref_request
