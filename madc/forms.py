# forms.py
# Standard Library
import re

# Django
from django import forms
from django.utils.translation import gettext_lazy as _


class DeleteForm(forms.Form):
    """Form for Deleting."""

    pk = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
        label="ID",
        help_text="The ID of the item to delete.",
    )


class SkillListForm(forms.Form):
    name = forms.CharField(
        required=True,
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Skill Plan Name",
        help_text="Enter a name for your skill plan.",
    )

    category = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Category",
        help_text="Enter a category for your skill plan (e.g., 'Combat', 'Industry').",
    )

    ordering = forms.IntegerField(
        required=False,
        initial=0,
        min_value=0,
        max_value=999,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
        label="Order Weight",
        help_text="Enter a weight for ordering this skill plan. Lower numbers appear first.",
    )

    skill_list = forms.CharField(
        required=True,
        max_length=10000,
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 10}),
        label="Skill List (Skillplan format)",
        help_text="Enter your skill list in Skillplan format. Example: Minmatar Destroyer 3, Minmatar Cruiser 4, etc. Each skill should be on a new line.",
    )

    def clean_skill_list(self):
        skill_list = self.cleaned_data["skill_list"]

        if not skill_list.strip():
            raise forms.ValidationError(_("Skill list cannot be empty."))

        lines = skill_list.strip().split("\n")

        # Pattern for plain format: "Skill Name Level"
        plain_pattern = re.compile(r"^(.+)\s+([1-5])$")

        # Pattern for localized format: '<localized hint="Skill Name">Skill Name*</localized> Level'
        localized_pattern = re.compile(
            r'^<localized hint="([^"]+)">[^<]*</localized>\s+([1-5])$'
        )

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:  # Skip empty lines
                continue

            # Try plain format first
            plain_match = plain_pattern.match(line)
            if plain_match:
                skill_name, __ = plain_match.groups()
                if not skill_name.strip():
                    raise forms.ValidationError(
                        _("Line {}: Skill name cannot be empty").format(line_num)
                    )
                continue

            # Try localized format
            localized_match = localized_pattern.match(line)
            if localized_match:
                skill_name, __ = localized_match.groups()
                if not skill_name.strip():
                    raise forms.ValidationError(
                        _("Line {}: Skill name cannot be empty").format(line_num)
                    )
                continue

            # If neither pattern matches, raise error
            raise forms.ValidationError(
                _(
                    "Line {}: '{}' - Invalid format. Use 'Skill Name Level' (Level 1-5) or EVE localized format"
                ).format(line_num, line[:50] + "..." if len(line) > 50 else line)
            )

        return skill_list

    def get_parsed_skills(self):
        """Extract skill names and levels from the validated skill list and return as dictionary with highest level per skill"""
        if not hasattr(self, "cleaned_data") or "skill_list" not in self.cleaned_data:
            return {}

        skill_list = self.cleaned_data["skill_list"]
        lines = skill_list.strip().split("\n")
        skills_dict = {}

        plain_pattern = re.compile(r"^(.+)\s+([1-5])$")
        localized_pattern = re.compile(
            r'^<localized hint="([^"]+)">[^<]*</localized>\s+([1-5])$'
        )

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try localized format FIRST to extract from hint
            localized_match = localized_pattern.match(line)
            if localized_match:
                skill_name, level = localized_match.groups()
                skill_name = skill_name.strip()
                level = int(level)

                # Keep the highest level for each skill
                if skill_name not in skills_dict or skills_dict[skill_name] < level:
                    skills_dict[skill_name] = level
                continue

            # Try plain format second
            plain_match = plain_pattern.match(line)
            if plain_match:
                skill_name, level = plain_match.groups()
                skill_name = skill_name.strip()
                level = int(level)

                # Keep the highest level for each skill
                if skill_name not in skills_dict or skills_dict[skill_name] < level:
                    skills_dict[skill_name] = level

        return skills_dict

    def clean_name(self):
        name = self.cleaned_data["name"]

        # pylint: disable=import-outside-toplevel
        # AA Memberaudit Doctrine Checker
        from madc.models.skillchecker import SkillList

        if SkillList.objects.filter(name=name).exists():
            raise forms.ValidationError(
                _(
                    "A skill plan with the name '{}' already exists. Please choose a different name."
                ).format(name)
            )

        return name
