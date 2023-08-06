from logging import debug
from cli_ui import warning, fatal

from gitlabform import EXIT_INVALID_INPUT
from gitlabform.gitlab import GitLab, AccessLevel
from gitlabform.processors.abstract_processor import AbstractProcessor


class GroupMembersProcessor(AbstractProcessor):
    def __init__(self, gitlab: GitLab):
        super().__init__("group_members", gitlab)

    def _section_is_in_config(self, configuration: dict):
        return any(
            section_name in configuration
            for section_name in [
                "group_members",
                "group_shared_with",
                "enforce_group_members",
            ]
        )

    def _process_configuration(self, group: str, configuration: dict):

        enforce_group_members = self._is_enforce_enabled(configuration)

        (
            groups_to_set_by_group_path,
            users_to_set_by_username,
        ) = self._get_groups_and_users_to_set(configuration)

        if (
            enforce_group_members
            and not groups_to_set_by_group_path
            and not users_to_set_by_username
        ):
            fatal(
                "Group members configuration section has to contain"
                " some 'users' or 'groups' defined as Owners,"
                " if you want to enforce them (GitLab requires it).",
                exit_code=EXIT_INVALID_INPUT,
            )

        self._process_groups(group, groups_to_set_by_group_path, enforce_group_members)

        self._process_users(group, users_to_set_by_username, enforce_group_members)

    @staticmethod
    def _is_enforce_enabled(configuration: dict) -> bool:

        # read if enforcing is enabled from the config once - it will be used for both sharing group with groups
        # as well as assigning single users to group

        enforce_group_members = configuration.get("enforce_group_members", False)
        if enforce_group_members:
            warning(
                "Using `enforce_group_members` key is deprecated and will be removed in future versions "
                "of GitLabForm. Please use `group_members.enforce` key instead."
            )
        else:
            enforce_group_members = configuration.get("group_members|enforce", False)
        return enforce_group_members

    @staticmethod
    def _get_groups_and_users_to_set(configuration: dict) -> (dict, dict):

        # read the configs in a single place, as the syntax is changing and there are a lot of possible
        # deprecation notices to be printed

        groups_to_set_by_group_path = configuration.get("group_shared_with", {})
        if groups_to_set_by_group_path:
            warning(
                "Using `group_shared_with:` is deprecated and will be removed in future versions "
                "of GitLabForm. Please move its contents to `group_members.groups`."
            )
        else:
            groups_to_set_by_group_path = configuration.get("group_members|groups", {})

        users_to_set_by_username = configuration.get("group_members", {})
        if users_to_set_by_username:
            proper_users_to_set_by_username = configuration.get(
                "group_members|users", {}
            )
            if proper_users_to_set_by_username:
                users_to_set_by_username = proper_users_to_set_by_username
            else:
                users_to_set_by_username.pop("enforce", None)
                users_to_set_by_username.pop("users", None)
                users_to_set_by_username.pop("groups", None)
                if users_to_set_by_username:
                    warning(
                        "Putting users as target members of the groups directly under `group_members` key is deprecated "
                        "and will be removed in future versions of GitLabForm. "
                        "Please put them under `group_members.users` key instead."
                    )

        return groups_to_set_by_group_path, users_to_set_by_username

    def _process_groups(
        self, group: str, groups_to_set_by_group_path: dict, enforce_group_members: bool
    ):

        # group users before by group name
        groups_before = self.gitlab.get_group_case_insensitive(group)[
            "shared_with_groups"
        ]
        debug("Group shared with BEFORE: %s", groups_before)

        groups_before_by_group_path = dict()
        for share_details in groups_before:
            groups_before_by_group_path[
                share_details["group_full_path"]
            ] = share_details

        for share_with_group_path in groups_to_set_by_group_path:

            group_access_to_set = groups_to_set_by_group_path[
                share_with_group_path
            ].get("group_access_level", None)
            if group_access_to_set:
                warning(
                    "Using `group_access_level` key deprecated and will be removed in future versions "
                    "of GitLabForm. Please rename it to `group_access`."
                )
            else:
                group_access_to_set = groups_to_set_by_group_path[
                    share_with_group_path
                ]["group_access"]

            expires_at_to_set = (
                groups_to_set_by_group_path[share_with_group_path]["expires_at"]
                if "expires_at" in groups_to_set_by_group_path[share_with_group_path]
                else None
            )

            if share_with_group_path in groups_before_by_group_path:

                group_access_before = groups_before_by_group_path[
                    share_with_group_path
                ]["group_access_level"]
                expires_at_before = groups_before_by_group_path[share_with_group_path][
                    "expires_at"
                ]

                if (
                    group_access_before == group_access_to_set
                    and expires_at_before == expires_at_to_set
                ):
                    debug(
                        "Nothing to change for group '%s' - same config now as to set.",
                        share_with_group_path,
                    )
                else:
                    debug(
                        "Re-adding group '%s' to change their access level or expires at.",
                        share_with_group_path,
                    )
                    # we will remove the group first and then re-add them,
                    # to ensure that the group has the expected access level
                    self.gitlab.remove_share_from_group(group, share_with_group_path)
                    self.gitlab.add_share_to_group(
                        group,
                        share_with_group_path,
                        group_access_to_set,
                        expires_at_to_set,
                    )

            else:
                debug(
                    "Adding group '%s' who previously was not a member.",
                    share_with_group_path,
                )
                self.gitlab.add_share_to_group(
                    group, share_with_group_path, group_access_to_set, expires_at_to_set
                )

        if enforce_group_members:
            # remove groups not configured explicitly
            groups_not_configured = set(groups_before_by_group_path) - set(
                groups_to_set_by_group_path
            )
            for group_path in groups_not_configured:
                debug(
                    "Removing group '%s' who is not configured to be a member.",
                    group_path,
                )
                self.gitlab.remove_share_from_group(group, group_path)
        else:
            debug("Not enforcing group members.")

        debug("Group shared with AFTER: %s", self.gitlab.get_group_members(group))

    def _process_users(
        self, group: str, users_to_set_by_username: dict, enforce_group_members: bool
    ):

        # group users before by username
        # (note: we DON'T get inherited users as we don't manage them at this level anyway)
        users_before = self.gitlab.get_group_members(group, with_inherited=False)
        debug("Group members BEFORE: %s", users_before)
        users_before_by_username = dict()
        for user in users_before:
            users_before_by_username[user["username"]] = user

        if users_to_set_by_username:

            # group users to set by access level
            users_to_set_by_access_level = dict()
            for user in users_to_set_by_username:
                access_level = users_to_set_by_username[user]["access_level"]
                users_to_set_by_access_level.setdefault(access_level, []).append(user)

            # we HAVE TO start configuring access from the highest access level - in case of groups this is Owner
            # - to ensure that we won't end up with no Owner in a group
            for level in reversed(sorted(AccessLevel.group_levels())):

                users_to_set_with_this_level = (
                    users_to_set_by_access_level[level]
                    if level in users_to_set_by_access_level
                    else []
                )

                for user in users_to_set_with_this_level:

                    access_level_to_set = users_to_set_by_username[user]["access_level"]
                    expires_at_to_set = (
                        users_to_set_by_username[user]["expires_at"]
                        if "expires_at" in users_to_set_by_username[user]
                        else None
                    )

                    if user in users_before_by_username:

                        access_level_before = users_before_by_username[user][
                            "access_level"
                        ]
                        expires_at_before = users_before_by_username[user]["expires_at"]

                        if (
                            access_level_before == access_level_to_set
                            and expires_at_before == expires_at_to_set
                        ):
                            debug(
                                "Nothing to change for user '%s' - same config now as to set.",
                                user,
                            )
                        else:
                            debug(
                                "Re-adding user '%s' to change their access level or expires at.",
                                user,
                            )
                            # we will remove the user first and then re-add they,
                            # to ensure that the user has the expected access level
                            self.gitlab.remove_member_from_group(group, user)
                            self.gitlab.add_member_to_group(
                                group, user, access_level_to_set, expires_at_to_set
                            )

                    else:
                        debug("Adding user '%s' who previously was not a member.", user)
                        self.gitlab.add_member_to_group(
                            group, user, access_level_to_set, expires_at_to_set
                        )

        if enforce_group_members:
            # remove users not configured explicitly
            # note: only direct members are removed - inherited are left
            users_not_configured = set(
                [user["username"] for user in users_before]
            ) - set(users_to_set_by_username.keys())
            for user in users_not_configured:
                debug("Removing user '%s' who is not configured to be a member.", user)
                self.gitlab.remove_member_from_group(group, user)
        else:
            debug("Not enforcing group members.")

        debug("Group members AFTER: %s", self.gitlab.get_group_members(group))
