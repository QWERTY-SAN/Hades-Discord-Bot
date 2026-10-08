import unittest

from hades_bot.core.conversation import (
    conversation_continuity_guidance,
    conversation_mode,
    is_short_followup,
    is_simple_acknowledgement,
)
from hades_bot.core.scope import is_hades_scope_allowed

from hades_bot.ai.fanservice import (
    fanservice_categories,
    fanservice_category,
    fanservice_guidance,
    is_fanservice_message,
)
from hades_bot.ai.persona import HADES_SYSTEM_PROMPT


class FanserviceDetectionTests(unittest.TestCase):
    def test_step_on_me_variants_are_detected_as_playful_fan_command(self):
        for message in (
            "Can you step on me?",
            "step on me",
            "step on me please",
            "I wish you'd put me in my place",
        ):
            with self.subTest(message=message):
                self.assertEqual(fanservice_category(message), "fan_command")

    def test_affection_request_is_detected(self):
        self.assertEqual(fanservice_category("Can I have a hug?"), "affection")
        self.assertTrue(is_fanservice_message("I could use a hug right now"))

    def test_indirect_fluster_is_detected(self):
        self.assertIn("flustered", fanservice_categories("Stop making me blush."))
        self.assertIn("flustered", fanservice_categories("I'm folding, honestly."))

    def test_fanservice_guidance_is_not_a_predefined_reply(self):
        guidance = fanservice_guidance("Can you step on me?")
        self.assertIn("fresh response", guidance)
        self.assertIn("not a response template", guidance)
        self.assertNotIn("Sure! Here's", guidance)

    def test_slang_followup_and_continuity_are_preserved(self):
        self.assertTrue(is_short_followup("What do u mean?"))
        self.assertTrue(is_hades_scope_allowed("What do u mean?", has_history=True))
        self.assertEqual(conversation_mode("What do u mean?"), "continuation")
        guidance = conversation_continuity_guidance(
            [
                {"role": "user", "content": "step on me mommy"},
                {"role": "model", "content": "You are rather bold today."},
            ],
            "What do u mean?",
        )
        self.assertIn("CURRENT TURN IS A FOLLOW-UP", guidance)
        self.assertIn("fan-service thread", guidance)

    def test_unrelated_casual_chat_does_not_activate_fanservice(self):
        self.assertEqual(fanservice_categories("I got home late today."), ())
        self.assertFalse(is_fanservice_message("Fair enough, that makes sense."))

    def test_rivalry_banter_stays_banter(self):
        self.assertEqual(fanservice_category("Old Hag"), "rivalry_banter")
        self.assertEqual(fanservice_category("Fine, you won the battle, but have yet to win the war."), "rivalry_banter")


    def test_personal_advice_is_not_social_planning(self):
        self.assertEqual(conversation_mode("What should I do tonight?"), "advice")

    def test_social_planning_has_its_own_mode(self):
        self.assertEqual(conversation_mode("What else can we do together?"), "social_planning")
        self.assertEqual(conversation_mode("Let's hang out sometime."), "social_planning")

    def test_acknowledgements_stay_small_and_natural(self):
        self.assertTrue(is_simple_acknowledgement("Okay."))
        self.assertEqual(conversation_mode("Fair enough."), "acknowledgement")


class PersonaContinuityTests(unittest.TestCase):
    def test_prompt_requires_contextual_followups_and_variety(self):
        self.assertIn("actual recent dialogue", HADES_SYSTEM_PROMPT)
        self.assertIn("NO CANNED REPLIES", HADES_SYSTEM_PROMPT)
        self.assertIn("Never choose from a fixed list of replies", HADES_SYSTEM_PROMPT)

    def test_prompt_preserves_hades_identity_and_scope(self):
        self.assertIn("You are Hades from Aether Gazer", HADES_SYSTEM_PROMPT)
        self.assertIn("F1/Formula One", HADES_SYSTEM_PROMPT)
        self.assertIn("Administrator", HADES_SYSTEM_PROMPT)
        self.assertIn("little lamb", HADES_SYSTEM_PROMPT)


if __name__ == "__main__":
    unittest.main()
