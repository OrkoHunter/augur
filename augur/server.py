#SPDX-License-Identifier: MIT
import os
import sys
import json
from flask import Flask, request, Response, send_from_directory
from flask_cors import CORS
import augur

sys.path.append('..')

AUGUR_API_VERSION = 'api/unstable'


'''
make a try and accept condition
if its open the GH_DATA_CONFIG_FILE and then its open in read mode
and if the file does't open the it print Couldn\'t open config file, attempting to create.
'''

class Server(object):
    def __init__(self):
        # Create Flask application
        self.app = Flask(__name__)
        app = self.app
        CORS(app)

        # Create Augur application
        self.augurApp = augur.Application()
        augurApp = self.augurApp

        # Initialize cache
        expire_minutes = int(augurApp.read_config('Server', 'cache_expire', 'AUGUR_CACHE_EXPIRE', 3600))
        self.cache = augurApp.cache.get_cache('server', expire=expire_minutes)
        self.cache.clear()

        # Initalize all of the classes
        ghtorrent = augurApp.ghtorrent()
        ghtorrentplus = augurApp.ghtorrentplus()
        publicwww = augurApp.publicwww()
        git = augurApp.git()
        github = augurApp.githubapi()
        librariesio = augurApp.librariesio()
        downloads = augurApp.downloads()
        localcsv = augurApp.localcsv()

        #####################################
        ###    DIVERSITY AND INCLUSION    ###
        #####################################


        #####################################
        ### GROWTH, MATURITY, AND DECLINE ###
        #####################################

        """
        @api {get} /:owner/:repo/timeseries/issues Issues
        @apiName Issues
        @apiGroup Growth-Maturity-Decline
        @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "issues":13
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "issues":15
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.issues, 'issues')

        """
        @api {get} /:owner/:repo/timeseries/issues/closed Issues Closed
        @apiName Issues
        @apiGroup Growth-Maturity-Decline

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                        [
                            {
                              "date": "2011-03-19T00:00:00.000Z",
                              "issues_closed": 3
                            },
                            {
                              "date": "2011-03-20T00:00:00.000Z",
                              "issues_closed": 0
                            }
                        ]
        """
        self.addTimeseries(ghtorrent.issues_closed, "issues/closed")

        """
        @api {get} /:owner/:repo/timeseries/issues/response_time Issue Response Time
        @apiName IssueResponseTime
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "created_at": "2013-09-16T17:00:54.000Z",
                                    "responded_at": "2013-09-16T17:20:58.000Z"
                                },
                                {
                                    "created_at": "2013-09-16T09:31:34.000Z",
                                    "responded_at": "2013-09-16T09:43:03.000Z"
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.issue_response_time, 'issues/response_time')

        """
        @api {get} /:owner/:repo/timeseries/commits?group_by=:group_by Commits
        @apiName Commits
        @apiGroup Growth-Maturity-Decline
        @apiDescription/github.<a href="com/chaoss/metrics/blob/master/activity-metrics/code-commits.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository
        @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "commits": 153
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "commits": 192
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.commits, 'commits')

        """
        @api {get} /:owner/:repo/timeseries/lines_changed Net number of lines of code changed
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/lines-of-code-changed.md">CHAOSS Metric Definition</a>
        @apiName LinesChanged
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    'date': '2015-11-01T00:00:00Z',
                                    'lines_changed': 396137.0
                                },
                                {
                                    'date': '2015-11-08T00:00:00Z',
                                    'lines_changed': 3896.0
                                },
                            ]
        """
        self.addTimeseries(github.lines_changed, 'lines_changed')

        """
        @api {get} /:owner/:repo/pulls/maintainer_response_time Time to First Maintainer Response to Merge Request
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md">CHAOSS Metric Definition</a>
        @apiName TimeToFirstMaintainerResponseToMergeRequest
        @apiGroup Growth-Maturity-Decline

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "response_time":11044366.0
                                },
                                {
                                    "response_time":11044955.0
                                },
                            ]
        """
        self.addTimeseries(ghtorrent.time_to_first_maintainer_response_to_merge_request, 'pulls/maintainer_response_time')

        """
        @api {get} /:owner/:repo/timeseries/forks?group_by=:group_by Forks
        @apiName Forks
        @apiGroup Growth-Maturity-Decline
        @apiParam {String} group_by (Default to week) Allows for results to be grouped by day, week, month, or year
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/forks.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "forks": 13
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "forks": 12
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.forks, 'forks')

        """
        @api {get} /:owner/:repo/timeseries/pulls Pull Requests by Week
        @apiName PullRequestsByWeek
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "pull_requests": 1
                                    "comments": 11
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "pull_requests": 2
                                    "comments": 31
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.pulls, 'pulls')

        """
        @api {get} /:owner/:repo/timeseries/pull_request_comments count of new pull request comments weekly
        @apiName PullRequestComments
        @apiGroup Growth-Maturity-Decline
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/pull-request-comments.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {   "date":"2009-02-16T00:00:00.000Z",
                                    "comments":1.0
                                },
                                {   "date":"2009-07-12T00:00:00.000Z",
                                    "comments":2.0
                                },

        """
        self.addTimeseries(ghtorrent.pull_request_comments, 'pulls/comments')

        self.addTimeseries(ghtorrent.code_review_iteration, 'code_review_iteration')

        self.addTimeseries(ghtorrent.contribution_acceptance, 'contribution_acceptance')

        self.addTimeseries(ghtorrent.new_contributing_github_organizations, 'new_contributing_github_organizations')

        self.addMetric(ghtorrent.contributing_github_organizations, 'contributing_github_organizations')

        # self.addTimeseries(github.code_reviews, 'code_reviews')

        #####################################
        ###            RISK               ###
        #####################################

        """
        @api {get} /:owner/:repo/bus_factor Bus Factor
        @apiName BusFactor
        @apiDescription Metric Undefined
        @apiDescription Returns an integer that is the number of developers that have a summed percentage of contributions higher than the threshold
        @apiName GitHub
        @apiGroup Activity

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "best": "5",
                                    "worst": "1"
                                }
                            ]
        """
        self.addMetric(github.bus_factor, 'bus_factor')

        #####################################
        ###            VALUE              ###
        #####################################


        #####################################
        ###           ACTIVITY            ###
        #####################################

        """
        @api {get} /:owner/:repo/timeseries/issue_comments Count of New Comments
        @apiName uniqueCommenters
        @apiGroup Activity
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {   "date":"2009-02-16T00:00:00.000Z",
                                    "total_unique_comments":1.0
                                },
                                {   "date":"2009-07-12T00:00:00.000Z",
                                    "total_unique_comments":2.0
                                },
                            ]
        """
        self.addTimeseries(ghtorrent.issue_comments, 'issue/comments')

        """
        @api {get} /:owner/:repo/watchers
        @apiName Community Engagement
        @apiGroup Users

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                              {
                                "watchers": 40349
                              }
                            ]
        """
        self.addMetric(ghtorrent.watchers, 'watchers')


        #####################################
        ###         EXPERIMENTAL          ###
        #####################################

        ### COMMIT RELATED ###
        #todo: document
        self.addTimeseries(ghtorrent.commits100, 'commits100')

        """
        @api {get} /:owner/:repo/timeseries/commits/comments count of commit comments weekly
        @apiName CommitComments
        @apiGroup Experimental
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-commits.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {   "date":"2009-02-16T00:00:00.000Z",
                                    "comments":1.0
                                },
                                {   "date":"2009-07-12T00:00:00.000Z",
                                    "comments":2.0
                                },

        """
        self.addTimeseries(ghtorrent.commit_comments, 'commits/comments')

        """
        @api {get} /:owner/:repo/timeseries/total_committers count of new committers weekly
        @apiName UniqueCommitters
        @apiDescription Metric Undefined
        @apiGroup Growth/Maturity-Decline

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {   "date":"2009-02-16T00:00:00.000Z",
                                    "total_total_committers":1.0
                                },
                                {   "date":"2009-07-12T00:00:00.000Z",
                                    "total_total_committers":2.0
                                },
                            ]
        """
        self.addTimeseries(ghtorrent.total_committers, 'total_committers')

        """
        @api {get} /:owner/:repo/committer_locations Commits and Location by User
        @apiName CommitterLocations
        @apiDescription Metric Undefined
        @apiGroup Diversity-Inclusion

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "login": "bonnie",
                                    "location": "Rowena, TX",
                                    "commits": 12
                                },
                                {
                                    "login":"clyde",
                                    "location":"Ellis County, TX",
                                    "commits": 12
                                }
                            ]
        """
        self.addMetric(ghtorrent.committer_locations, 'committer_locations')


        ### ISSUE RELATED ###
        """
        @api {get} /:owner/:repo/timeseries/issues/activity Issues Activity
        @apiName Issues
        @apiGroup Experimental
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/first-response-to-issue-duration.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                  "date": "2010-12-23T00:00:00.000Z",
                                  "count": 0.0,
                                  "action": "closed"
                                },
                                {
                                  "date": "2010-12-23T00:00:00.000Z",
                                  "count": 2.0,
                                  "action": "opened"
                                },
                                {
                                  "date": "2010-12-23T00:00:00.000Z",
                                  "count": 8.0,
                                  "action": "reopened"
                                },
                                {
                                  "date": "2010-12-23T00:00:00.000Z",
                                  "count": 12.0,
                                  "action": "open"
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.issue_activity, 'issues/activity')

        """
        @api {get} /:owner/:repo/issue_close_time Issue Close Time
        @apiName Issues
        @apiGroup Experimental
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issue-resolution-efficiency.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                        [
                            {
                              "id": 136603,
                              "repo_id": 1334,
                              "opened": "2010-09-08 19:09:56",
                              "pull_request": 1,
                              "minutes_to_close": 1264.0,
                              "average_minutes_to_close_as_of_close": 1264.0,
                              "average_minutes_to_close_past_30_days": 1264.0,
                              "z-score": -0.3152279792
                            },
                            {
                              "id": 136602,
                              "repo_id": 1334,
                              "opened": "2010-09-09 04:33:23",
                              "pull_request": 1,
                              "minutes_to_close": 701.0,
                              "average_minutes_to_close_as_of_close": 982.5,
                              "average_minutes_to_close_past_30_days": 982.5,
                              "z-score": -0.3184596776
                            }
                        ]
        """
        self.addMetric(ghtorrentplus.issue_close_time, 'issue_close_time')


        # PULL REQUEST RELATED
        """
        @api {get} /:owner/:repo/timeseries/pulls/acceptance_rate Pull Request Acceptance Rate by Week
        @apiDescription For each week, the rate is calculated as (pull requests merged that week) / (pull requests opened that week).
        @apiName PullRequestAcceptanceRate
        @apiGroup Experimental
        @apiDescription <a href="incomplete): https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "rate": 0.5
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "rate": 0.33
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.pull_acceptance_rate, 'pulls/acceptance_rate')


        # COMMUNITY / CONTRIBUTIONS
        """
        @api {get} /:owner/:repo/timeseries/community_engagement
        @apiName Community Engagement
        @apiGroup Experimental
        @apiDescription <a href="https://github.com/chaoss/metrics/blob/master/activity-metrics/issues-submitted-closed.md">CHAOSS Metric Definition</a>
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                  "date": "2009-04-01T00:00:00.000Z",
                                  "issues_opened": 1.0,
                                  "issues_closed": 0.0,
                                  "pull_requests_opened": 0.0,
                                  "pull_requests_merged": 0.0,
                                  "pull_requests_closed": 0.0,
                                  "issues_opened_total": 2.0,
                                  "issues_closed_total": 0.0,
                                  "issues_closed_rate_this_window": 0.0,
                                  "issues_closed_rate_total": 0.0,
                                  "issues_delta": 1.0,
                                  "issues_open": 2.0,
                                  "pull_requests_opened_total": 0.0,
                                  "pull_requests_closed_total": 0.0,
                                  "pull_requests_closed_rate_this_window": null,
                                  "pull_requests_closed_rate_total": null,
                                  "pull_requests_delta": 0.0,
                                  "pull_requests_open": 0.0
                                },
                                {
                                  "date": "2009-04-16T00:00:00.000Z",
                                  "issues_opened": 2.0,
                                  "issues_closed": 1.0,
                                  "pull_requests_opened": 1.0,
                                  "pull_requests_merged": 1.0,
                                  "pull_requests_closed": 1.0,
                                  "issues_opened_total": 3.0,
                                  "issues_closed_total": 5.0,
                                  "issues_closed_rate_this_window": 4.0,
                                  "issues_closed_rate_total": 6.0,
                                  "issues_delta": 1.0,
                                  "issues_open": 2.0,
                                  "pull_requests_opened_total": 3.0,
                                  "pull_requests_closed_total": 5.0,
                                  "pull_requests_closed_rate_this_window": null,
                                  "pull_requests_closed_rate_total": null,
                                  "pull_requests_delta": 2.0,
                                  "pull_requests_open": 1.0
                                }
                            ]
        """
        self.addTimeseries(ghtorrent.community_engagement, 'community_engagement')

        """
        @api {get} /:owner/:repo/timeseries/community_age Timeline of events to determine the age of a community
        @apiName CommunityAge
        @apiDescription Metric Undefined
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "login": "bonnie",
                                    "location": "Rowena, TX",
                                    "commits": 12
                                },
                                {
                                    "login":"clyde",
                                    "location":"Ellis County, TX",
                                    "commits": 12
                                }
                            ]
        """
        self.addMetric(ghtorrent.community_age, 'community_age')

        """
        @api {get} /:owner/:repo/contributors Total Contributions by User
        @apiName TotalContributions
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/contributors.md">CHAOSS Metric Definition</a>
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                           [
                                {
                                    "login": "foo",
                                    "location": "Springfield",
                                    "commits": 1337.0,
                                    "pull_requests": 60.0,
                                    "issues": null,
                                    "commit_comments": 158.0,
                                    "pull_request_comments": 718.0,
                                    "issue_comments": 1668.0
                                },
                                {
                                    "login": "bar",
                                    "location": null,
                                    "commits": 3968.0,
                                    "pull_requests": null,
                                    "issues": 12.0,
                                    "commit_comments": 158.0,
                                    "pull_request_comments": 718.0,
                                    "issue_comments": 1568.0
                                }
                            ]
        """
        self.addMetric(ghtorrent.contributors, 'contributors')

        """
        @api {get} /:owner/:repo/timeseries/contributions Contributions by Week
        @apiName ContributionsByWeek
        @apiDescription <a href="https://github.com/OSSHealth/metrics/blob/master/activity-metrics/contributors.md">CHAOSS Metric Definition</a>
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository
        @apiParam (String) user Limit results to the given user's contributions

        @apiSuccessExample {json} Success-Response:
                           [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "commits": 37.0,
                                    "pull_requests": null,
                                    "issues": null,
                                    "commit_comments": 7.0,
                                    "pull_request_comments": 8.0,
                                    "issue_comments": 17.0
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "commits": 68.0,
                                    "pull_requests": null,
                                    "issues": 12.0,
                                    "commit_comments": 18.0,
                                    "pull_request_comments": 13.0,
                                    "issue_comments": 28.0
                                }
                            ]
        """
        @app.route('/{}/<owner>/<repo>/contributions'.format(AUGUR_API_VERSION))
        def contributions(owner, repo):
            repoid = ghtorrent.repoid(owner_or_repoid=owner, repo=repo)
            user = request.args.get('user')
            if (user):
                userid = ghtorrent.userid(username=user)
                contribs = ghtorrent.contributions(repoid, userid)
            else:
                contribs = ghtorrent.contributions(repoid)
            serialized_contributors = self.serialize(contribs, orient=request.args.get('orient'))
            return Response(response=serialized_contributors,
                            status=200,
                            mimetype="application/json")


        ### DEPENDENCY RELATED ###
        """
        @api {get} /:owner/:repo/dependencies List of dependencies from libraries.io
        @apiName Dependencies
        @apiDescription Metric Undefined
        @apiGroup Risk

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {   "full_name": "rails/rails"
                                    "description": "Ruby on Rails",
                                    "fork": false, "created_at": "2008-04-11T02:19:47.000Z",
                                    "updated_at": "2017-09-20T20:16:47.181Z",
                                    "pushed_at": "2017-09-20T19:39:08.000Z",
                                    "homepage": "http://rubyonrails.org",
                                    "size": 155199, "stargazers_count": 36993,
                                    "language": "Ruby", "has_issues": true,
                                    "has_wiki": false,
                                    "has_pages": false,
                                    "forks_count": 15130,
                                    "mirror_url": null,
                                    "open_issues_count": 1157,
                                    "default_branch": "master",
                                    "subscribers_count": 2452,
                                    "uuid": "8514", "source_name": null,
                                    "license": "MIT", "private": false,
                                    "contributions_count": 2616,
                                    "has_readme": "README.md",
                                    "has_changelog": null,
                                    "has_contributing": "CONTRIBUTING.md",
                                    "has_license": "MIT-LICENSE",
                                    "has_coc": "CODE_OF_CONDUCT.md",
                                    "has_threat_model": null,
                                    "has_audit": null,
                                    "status": null,
                                    "last_synced_at": "2017-09-20T20:16:47.153Z",
                                    "rank": 28, "host_type": "GitHub",
                                    "host_domain": null,
                                    "name": null,
                                    "scm": "git",
                                    "fork_policy": null,
                                     "github_id": "8514",
                                     "pull_requests_enabled": null,
                                     "logo_url": null,
                                     "github_contributions_count": 2616,
                                     "keywords": ["activejob", "activerecord", "html", "mvc", "rails", "ruby"],
                                     "dependencies": [
                                                        {   "project_name": "websocket-driver",
                                                            "name": "websocket-driver",
                                                            "platform": "rubygems",
                                                            "requirements": "~> 0.6.1",
                                                            "latest_stable": "0.7.0",
                                                            "latest": "0.7.0",
                                                            "deprecated": false, "outdated": true,
                                                            "filepath": "actioncable/actioncable.gemspec", "
                                                            kind": "runtime"
                                                        }
                                                     ]
        """
        self.addMetric(librariesio.dependencies, 'dependencies')

        """
        @api {get} /:owner/:repo/dependents List of dependants from libraries.io
        @apiName Dependents
        @apiDescription Metric Undefined
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "login": "bonnie",
                                    "location": "Rowena, TX",
                                    "commits": 12
                                },
                                {
                                    "login":"clyde",
                                    "location":"Ellis County, TX",
                                    "commits": 12
                                }
                            ]
        """
        self.addMetric(librariesio.dependents, 'dependents')

        """
        @api {get} /:owner/:repo/dependency_stats List of libraries.io stats
        @apiName DependencyStats
        @apiGroup Risk

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "dependencies": "10",
                                    "dependent_projects": "10.6K",
                                    "dependent_repositories": "392K"
                                }
                            ]
        """
        self.addMetric(librariesio.dependency_stats, 'dependency_stats')



        ### OTHER ###
        """
        @api {get} /:owner/:repo/timeseries/downloads Number of downloads
        @apiDescription Timeseries of downloads from package manager
        @apiName Downloads
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "downlads": 235
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "dowloads": 327
                                }
                            ]
        """
        self.addTimeseries(downloads.downloads, 'downloads')

        #todo: documentation
        self.addTimeseries(ghtorrent.fakes, 'fakes')

        """
        @api {get} /:owner/:repo/timeseries/tags Tags release timeseries
        @apiDescription Timeseries of tags
        @apiName Tags
        @apiGroup Experimental
        @apiDescription Metric Undefined
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "release": 0.5
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "release": 0.5.1
                                }
                            ]
        """
        self.addTimeseries(github.tags, 'tags')

        """
        @api {get} /:owner/:repo/timeseries/tags/major Tags for major releases timeseries
        @apiDescription Timeseries of Major release tags
        @apiName Major Release Tags
        @apiGroup Experimental
        @apiDescription Metric Undefined
        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "date": "2015-01-01T00:00:00.000Z",
                                    "release": 1.0.0
                                },
                                {
                                    "date": "2015-01-08T00:00:00.000Z",
                                    "release": 2.0.0
                                }
                            ]
        """
        self.addTimeseries(github.major_tags, 'tags/major')

        """
        @api {get} /:owner/:repo/linking_websites Linking Websites
        @apiName LinkingWebsites
        @apiDescription Returns an array of websites and their rank according to http://publicwww.com/
        @apiGroup Experimental

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "url": "missouri.edu",
                                    "rank": "1"
                                },
                                {
                                    "url": "unomaha.edu",
                                    "rank": "2"
                                }
                            ]
        """
        self.addMetric(publicwww.linking_websites, 'linking_websites')

        """
        @api {get} /ghtorrent_range Range of dates covered by GHTorrent
        @apiName GhtorrentRange
        @apiGroup Utility
        """
        @app.route('/{}/ghtorrent_range'.format(AUGUR_API_VERSION))

        def ghtorrent_range():
            ghtorrent_range = self.serialize(ghtorrent.ghtorrent_range())
            return Response(response=ghtorrent_range,
                            status=200,
                            mimetype="application/json")


        #######################
        #         Git         #
        #######################

        """
        @api {get} /git/repos Git Repos
        @apiName Git Repos
        @apiDescription Shows downloaded Git repos
        @apiGroup Utility

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "best": "5",
                                    "worst": "1"
                                }
                            ]
        """
        @app.route('/{}/git/repos'.format(AUGUR_API_VERSION))
        def downloaded_repos():
            drs = self.serialize(git.downloaded_repos())
            return Response(response=drs,
                            status=200,
                            mimetype="application/json")

        """
        @api {get} /git/lines_changed/:git_repo_url Lines Changed
        @apiName Lines Changed (no whitespace)
        @apiDescription Shows detailed information about each file changed by each commit
        @apiGroup Uncategorized

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "additions":2,
                                    "author_date":"2018-05-14 10:09:57 -0500",
                                    "author_email":"s@goggins.com",
                                    "author_name":"Sean P. Goggins",
                                    "commit_date":"2018-05-16 10:12:22 -0500",
                                    "committer_email":"derek@howderek.com",
                                    "committer_name":"Derek Howard",
                                    "deletions":0,
                                    "hash":"77e603a",
                                    "message":"merge dev",
                                    "parents":"b8ec0ed"
                                }
                            ]
        """
        self.addGitMetric(git.lines_changed_minus_whitespace, 'lines_changed')

        """
        @api {get} /git/changes_by_author/:git_repo_url Changes by Author
        @apiName Changes by Author
        @apiDescription Shows total changes by author
        @apiGroup Uncategorized

        @apiParam {String} owner Username of the owner of the GitHub repository
        @apiParam {String} repo Name of the GitHub repository

        @apiSuccessExample {json} Success-Response:
                            [
                                {
                                    "additions":32142,
                                    "deletions":34232,
                                    "author_email":"derek@howderek.com",
                                    "author_name":"Derek Howard",
                                }
                            ]
        """
        self.addGitMetric(git.changes_by_author, 'changes_by_author')



        #######################
        #   Batch Requests    #
        #######################

        """
        @api {post} /batch Bus Factor
        @apiDescription Returns results of batch requests
        @apiName Batch
        @apiGroup Batch

        POST JSON of api requests
        """
        #TODO: documentation
        @app.route('/{}/batch'.format(AUGUR_API_VERSION), methods=['GET', 'POST'])
        def batch():
            """
            Execute multiple requests, submitted as a batch.

            :statuscode 207: Multi status
            """
            if request.method == 'GET':
                """this will return sensible defaults in the future"""
                return app.make_response('{"status": "501", "response": "Defaults for batch requests not implemented. Please POST a JSON array of requests to this endpoint for now."}')

            try:
                requests = json.loads(request.data)
            except ValueError as e:
                request.abort(400)

            responses = []

            for index, req in enumerate(requests):


                method = req['method']
                path = req['path']
                body = req.get('body', None)

                try:

                    with app.app_context():
                        with app.test_request_context(path,
                                                      method=method,
                                                      data=body):
                            try:
                                # Can modify flask.g here without affecting
                                # flask.g of the root request for the batch

                                # Pre process Request
                                rv = app.preprocess_request()

                                if rv is None:
                                    # Main Dispatch
                                    rv = app.dispatch_request()

                            except Exception as e:
                                rv = app.handle_user_exception(e)

                            response = app.make_response(rv)

                            # Post process Request
                            response = app.process_response(response)

                    # Response is a Flask response object.
                    # _read_response(response) reads response.response
                    # and returns a string. If your endpoints return JSON object,
                    # this string would be the response as a JSON string.
                    responses.append({
                        "path": path,
                        "status": response.status_code,
                        "response": str(response.get_data(), 'utf8')
                    })

                except Exception as e:

                    responses.append({
                        "path": path,
                        "status": 500,
                        "response": str(e)
                    })


            return Response(response=json.dumps(responses),
                            status=207,
                            mimetype="application/json")

        augurApp.finalize_config()

    def addMetric(self, function, endpoint, cache=True):
        """Simplifies adding routes that only accept owner/repo"""
        self.app.route('/{}/<owner>/<repo>/{}'.format(AUGUR_API_VERSION, endpoint))(self.flaskify(function, cache=cache))

    def addGitMetric(self, function, endpoint, cache=True):
        """Simplifies adding routes that accept"""
        self.app.route('/{}/git/{}/<path:repo_url>/'.format(AUGUR_API_VERSION, endpoint))(self.flaskify(function, cache=cache))

    def addTimeseries(self, function, endpoint):
        """
        Simplifies adding routes that accept owner/repo and return timeseries

        :param app:       Flask app
        :param function:  Function from a datasource to add
        :param endpoint:  GET endpoint to generate
        """
        self.addMetric(function, 'timeseries/{}'.format(endpoint))

    def serialize(self, data, orient='records'):

        if orient is None:
            orient = 'records'

        result = ''

        if hasattr(data, 'to_json'):
            result = data.to_json(orient=orient, date_format='iso', date_unit='ms')
        else:
            try:
                result = json.dumps(data)
            except:
                result = data

        return result

    def flaskify(self, func, cache=True):
        """
        Simplifies API endpoints that just accept owner and repo,
        serializes them and spits them out
        """
        if cache:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                def heavy_lifting():
                    return self.serialize(func(*args, **kwargs))
                body = self.cache.get(key=str(request.path), createfunc=heavy_lifting)
                return Response(response=body,
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__name__
            return generated_function
        else:
            def generated_function(*args, **kwargs):
                kwargs.update(request.args.to_dict())
                return Response(response=self.serialize(func(*args, **kwargs)),
                                status=200,
                                mimetype="application/json")
            generated_function.__name__ = func.__name__
            return generated_function



def run():
    server = Server()
    host = server.augurApp.read_config('Server', 'host', 'AUGUR_HOST', '0.0.0.0')
    port = server.augurApp.read_config('Server', 'port', 'AUGUR_PORT', '5000')
    Server().app.run(host=host, port=int(port))

wsgi_app = None
def wsgi(env, start_response):
    global wsgi_app
    if (wsgi_app is None):
        app_instance = Server()
        wsgi_app = app_instance.app
    return wsgi_app(env, start_response)

if __name__ == "__main__":
    run()
