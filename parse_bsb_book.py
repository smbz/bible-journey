#!/usr/bin/env python3
"""
Parse BSB (Berean Standard Bible) text and generate JavaScript data files
with manually defined paragraph structures.
"""

import urllib.request
import json
import re
import sys

global in_dialogue
in_dialogue = False

# Book configurations
BOOK_CONFIGS = {
    'mark': {
        'full_name': 'Gospel of Mark',
        'short_name': 'Mark',
        'start_pattern': r'^Mark 1:1',
        'end_pattern': r'^(Luke|Acts) 1:1',
        'chapters': 16,
        'paragraph_structure': {
            1: [
                [1, 2, 3],        # Prologue
                [4, 5, 6],        # John's ministry
                [7, 8],           # John's proclamation
                [9, 10, 11],      # Jesus's baptism
                [12, 13],         # Temptation
                [14, 15],         # Beginning of ministry
                [16, 17, 18],     # Calling first disciples
                [19, 20],         # James and John called
                [21, 22, 23, 24, 25, 26, 27, 28], # Demon in synagogue
                [29, 30, 31],     # Peter's mother-in-law healed
                [32, 33, 34],     # Evening healings
                [35, 36, 37, 38, 39], # Morning prayer and preaching
                [40, 41, 42, 43, 44, 45] # Healing leper
            ],
            2: [
                [1, 2, 3, 4, 5],  # Paralytic healed
                [6, 7, 8, 9, 10, 11, 12], # Faith and forgiveness
                [13, 14],         # Calling Levi
                [15, 16, 17],     # Eating with sinners
                [18, 19, 20],     # Question about fasting
                [21, 22],         # New wine in old wineskins
                [23, 24, 25, 26, 27, 28] # Lord of the Sabbath
            ],
            3: [
                [1, 2, 3, 4, 5, 6], # Healing on Sabbath
                [7, 8, 9, 10, 11, 12], # Crowds follow
                [13, 14, 15, 16, 17, 18, 19], # Appointing the Twelve
                [20, 21],         # Jesus and Beelzebul
                [22, 23, 24, 25, 26, 27], # A house divided
                [28, 29, 30],     # Unpardonable sin
                [31, 32, 33, 34, 35] # Jesus's mother and brothers
            ],
            4: [
                [1, 2],           # Parable of the Sower intro
                [3, 4, 5, 6, 7, 8, 9], # The parable
                [10, 11, 12],     # Purpose of parables
                [13, 14, 15, 16, 17, 18, 19, 20], # Explanation
                [21, 22, 23, 24, 25], # Lamp on a stand
                [26, 27, 28, 29], # Parable of growing seed
                [30, 31, 32],     # Parable of mustard seed
                [33, 34],         # Speaking in parables
                [35, 36, 37, 38, 39, 40, 41] # Calming the storm
            ],
            5: [
                [1, 2, 3, 4, 5],  # Gerasene demoniac
                [6, 7, 8, 9, 10], # Confrontation
                [11, 12, 13],     # Demons enter pigs
                [14, 15, 16, 17], # People's reaction
                [18, 19, 20],     # Man's testimony
                [21, 22, 23, 24], # Jairus's request
                [25, 26, 27, 28, 29], # Woman with bleeding
                [30, 31, 32, 33, 34], # Her healing
                [35, 36, 37, 38, 39, 40, 41, 42, 43] # Jairus's daughter raised
            ],
            6: [
                [1, 2, 3, 4, 5, 6], # Rejection at Nazareth
                [7, 8, 9, 10, 11, 12, 13], # Sending out the Twelve
                [14, 15, 16],     # Herod hears of Jesus
                [17, 18, 19, 20], # John's execution
                [21, 22, 23, 24, 25, 26, 27, 28, 29], # The beheading
                [30, 31, 32],     # Apostles return
                [33, 34],         # Crowds follow
                [35, 36, 37, 38, 39, 40, 41, 42, 43, 44], # Feeding 5000
                [45, 46, 47, 48, 49, 50, 51, 52], # Walking on water
                [53, 54, 55, 56] # Healings at Gennesaret
            ],
            7: [
                [1, 2, 3, 4, 5],  # Tradition of elders
                [6, 7, 8, 9, 10, 11, 12, 13], # Jesus rebukes Pharisees
                [14, 15, 16],     # What defiles
                [17, 18, 19, 20, 21, 22, 23], # Explanation
                [24, 25, 26],     # Syrophoenician woman
                [27, 28, 29, 30], # Her faith
                [31, 32, 33, 34, 35, 36, 37] # Healing deaf and mute
            ],
            8: [
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], # Feeding 4000
                [11, 12, 13],     # Pharisees demand sign
                [14, 15, 16, 17, 18, 19, 20, 21], # Yeast of Pharisees
                [22, 23, 24, 25, 26], # Healing blind man
                [27, 28, 29, 30], # Peter's confession
                [31, 32, 33],     # Jesus predicts death
                [34, 35, 36, 37, 38] # Cost of discipleship
            ],
            9: [
                [1],              # Kingdom coming with power
                [2, 3, 4, 5, 6, 7, 8], # Transfiguration
                [9, 10],          # Coming down mountain
                [11, 12, 13],     # Elijah has come
                [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29], # Boy with evil spirit
                [30, 31, 32],     # Second prediction of death
                [33, 34, 35, 36, 37], # Greatest in kingdom
                [38, 39, 40],     # Whoever is not against us
                [41, 42],         # Causing to stumble
                [43, 44, 45, 46, 47, 48, 49, 50] # Salt and fire
            ],
            10: [
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # Divorce
                [13, 14, 15, 16], # Little children
                [17, 18, 19, 20, 21, 22], # Rich young man
                [23, 24, 25, 26, 27], # Discussion of riches
                [28, 29, 30, 31], # Rewards of following
                [32, 33, 34],     # Third prediction
                [35, 36, 37, 38, 39, 40], # James and John's request
                [41, 42, 43, 44, 45], # Greatness in service
                [46, 47, 48, 49, 50, 51, 52] # Blind Bartimaeus
            ],
            11: [
                [1, 2, 3, 4, 5, 6, 7], # Triumphal entry preparation
                [8, 9, 10, 11],   # Entry into Jerusalem
                [12, 13, 14],     # Cursing fig tree
                [15, 16, 17, 18, 19], # Cleansing temple
                [20, 21, 22, 23, 24, 25, 26], # Withered fig tree
                [27, 28, 29, 30, 31, 32, 33] # Authority questioned
            ],
            12: [
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], # Parable of tenants
                [13, 14, 15, 16, 17], # Taxes to Caesar
                [18, 19, 20, 21, 22, 23, 24, 25, 26, 27], # Marriage and resurrection
                [28, 29, 30, 31, 32, 33, 34], # Greatest commandment
                [35, 36, 37],     # Whose son is Christ
                [38, 39, 40],     # Beware the scribes
                [41, 42, 43, 44]  # Widow's offering
            ],
            13: [
                [1, 2],           # Temple destruction predicted
                [3, 4, 5, 6, 7, 8], # Signs of end times
                [9, 10, 11, 12, 13], # Persecution coming
                [14, 15, 16, 17, 18, 19, 20], # Great tribulation
                [21, 22, 23],     # False christs
                [24, 25, 26, 27], # Son of Man coming
                [28, 29, 30, 31], # Parable of fig tree
                [32, 33, 34, 35, 36, 37] # Stay alert
            ],
            14: [
                [1, 2],           # Plot to kill Jesus
                [3, 4, 5, 6, 7, 8, 9], # Anointing at Bethany
                [10, 11],         # Judas agrees to betray
                [12, 13, 14, 15, 16], # Passover preparation
                [17, 18, 19, 20, 21], # Betrayer identified
                [22, 23, 24, 25, 26], # Lord's Supper
                [27, 28, 29, 30, 31], # Peter's denial predicted
                [32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42], # Gethsemane
                [43, 44, 45, 46, 47, 48, 49, 50, 51, 52], # Arrest
                [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65], # Trial before Sanhedrin
                [66, 67, 68, 69, 70, 71, 72] # Peter's denial
            ],
            15: [
                [1, 2, 3, 4, 5], # Trial before Pilate
                [6, 7, 8, 9, 10, 11, 12, 13, 14, 15], # Barabbas released
                [16, 17, 18, 19, 20], # Soldiers mock Jesus
                [21, 22, 23, 24, 25, 26, 27], # The crucifixion
                [28, 29, 30, 31, 32], # Mocking on cross
                [33, 34, 35, 36, 37, 38, 39], # Death of Jesus
                [40, 41],         # Women watching
                [42, 43, 44, 45, 46, 47] # Burial
            ],
            16: [
                [1, 2, 3, 4, 5, 6, 7, 8], # Empty tomb
                [9, 10, 11],      # Appears to Mary
                [12, 13],         # Appears to two
                [14, 15, 16, 17, 18], # Great Commission
                [19, 20]          # Ascension
            ]
        }
    },
    'luke': {
        'full_name': 'Gospel of Luke',
        'short_name': 'Luke',
        'start_pattern': r'^Luke 1:1',
        'end_pattern': r'^John 1:1',
        'chapters': 24,
        'paragraph_structure': {
            1: [
                [1, 2, 3, 4],  # Prologue to Theophilus
                [5, 6, 7],  # Zechariah and Elizabeth introduced
                [8, 9, 10],  # Zechariah at temple
                [11, 12, 13],  # Angel appears
                [14, 15, 16, 17],  # John's mission foretold
                [18, 19, 20],  # Zechariah's doubt
                [21, 22, 23],  # People waiting, Zechariah returns
                [24, 25],  # Elizabeth conceives
                [26, 27, 28],  # Gabriel sent to Mary
                [29, 30, 31, 32, 33],  # Annunciation
                [34, 35, 36, 37, 38],  # Mary's question and consent
                [39, 40, 41],  # Visitation begins
                [42, 43, 44, 45],  # Elizabeth's blessing
                [46, 47, 48, 49, 50, 51, 52, 53, 54, 55],  # Magnificat
                [56],  # Mary stays three months
                [57, 58],  # John's birth
                [59, 60, 61, 62, 63, 64],  # Naming of John
                [65, 66],  # People's reaction
                [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79],  # Benedictus
                [80]  # John's growth
            ],
            2: [
                [1, 2, 3],  # Census decree
                [4, 5],  # Journey to Bethlehem
                [6, 7],  # Birth of Jesus
                [8, 9],  # Shepherds in fields
                [10, 11, 12],  # Angel's announcement
                [13, 14],  # Heavenly host
                [15, 16],  # Shepherds visit
                [17, 18, 19, 20],  # Shepherds spread the news
                [21],  # Circumcision and naming
                [22, 23, 24],  # Presentation at temple
                [25, 26, 27],  # Simeon introduced
                [28, 29, 30, 31, 32],  # Nunc Dimittis
                [33, 34, 35],  # Simeon's prophecy
                [36, 37, 38],  # Anna the prophetess
                [39, 40],  # Return to Nazareth
                [41, 42, 43],  # Boy Jesus at temple
                [44, 45],  # Parents search
                [46, 47, 48],  # Found in temple
                [49, 50],  # Jesus's response
                [51, 52]  # Growth in Nazareth
            ],
            3: [
                [1, 2],  # Historical setting
                [3, 4, 5, 6],  # John's ministry
                [7, 8, 9],  # Warning to crowds
                [10, 11],  # Teaching crowds
                [12, 13],  # Teaching tax collectors
                [14],  # Teaching soldiers
                [15, 16, 17],  # Prophecy of Coming One
                [18],  # Summary of preaching
                [19, 20],  # John imprisoned
                [21, 22],  # Jesus baptized
                [23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38]  # Genealogy of Jesus
            ],
            4: [
                [1, 2],  # Led by Spirit to wilderness
                [3, 4],  # First temptation
                [5, 6, 7, 8],  # Second temptation
                [9, 10, 11, 12, 13],  # Third temptation
                [14, 15],  # Return to Galilee
                [16, 17, 18, 19, 20, 21],  # Nazareth synagogue
                [22, 23, 24],  # People's response
                [25, 26, 27],  # Elijah and Elisha
                [28, 29, 30],  # Rejection at Nazareth
                [31, 32],  # Teaching at Capernaum
                [33, 34, 35, 36, 37],  # Man with unclean spirit
                [38, 39],  # Peter's mother-in-law
                [40, 41],  # Healing many
                [42, 43, 44]  # Preaching tour
            ],
            5: [
                [1, 2, 3],  # Teaching from boat
                [4, 5, 6, 7],  # Miraculous catch
                [8, 9, 10, 11],  # Calling first disciples
                [12, 13, 14, 15, 16],  # Healing leper
                [17, 18, 19, 20],  # Paralytic lowered through roof
                [21, 22, 23, 24, 25, 26],  # Forgiveness and healing
                [27, 28],  # Calling Levi
                [29, 30, 31, 32],  # Banquet at Levi's house
                [33, 34, 35],  # Question about fasting
                [36, 37, 38, 39]  # Parables about new and old
            ],
            6: [
                [1, 2, 3, 4, 5],  # Lord of Sabbath
                [6, 7, 8, 9, 10, 11],  # Healing on Sabbath
                [12, 13, 14, 15, 16],  # Choosing the Twelve
                [17, 18, 19],  # Crowds gather
                [20, 21, 22, 23],  # Blessings
                [24, 25, 26],  # Woes
                [27, 28, 29, 30],  # Love your enemies
                [31, 32, 33, 34, 35, 36],  # Love and lend
                [37, 38],  # Do not judge
                [39, 40],  # Blind leading blind
                [41, 42],  # Speck and plank
                [43, 44, 45],  # Tree and fruit
                [46, 47, 48, 49]  # Wise and foolish builders
            ],
            7: [
                [1, 2, 3, 4, 5],  # Centurion's servant
                [6, 7, 8, 9, 10],  # Faith of centurion
                [11, 12, 13, 14, 15],  # Widow's son raised
                [16, 17],  # People's response
                [18, 19, 20],  # John's question
                [21, 22, 23],  # Jesus's answer
                [24, 25, 26, 27, 28],  # Jesus speaks about John
                [29, 30],  # People's responses
                [31, 32, 33, 34, 35],  # This generation
                [36, 37, 38],  # Sinful woman anoints
                [39, 40, 41, 42, 43],  # Parable of two debtors
                [44, 45, 46, 47],  # Contrasting responses
                [48, 49, 50]  # Your sins are forgiven
            ],
            8: [
                [1, 2, 3],  # Women supporting Jesus
                [4, 5, 6, 7, 8],  # Parable of sower
                [9, 10],  # Why parables
                [11, 12, 13, 14, 15],  # Explanation of sower
                [16, 17, 18],  # Lamp on stand
                [19, 20, 21],  # Jesus's mother and brothers
                [22, 23, 24, 25],  # Calming the storm
                [26, 27, 28, 29],  # Gerasene demoniac
                [30, 31, 32, 33],  # Legion enters pigs
                [34, 35, 36, 37],  # People's response
                [38, 39],  # Man testifies
                [40, 41, 42],  # Jairus's plea
                [43, 44, 45, 46, 47, 48],  # Woman healed
                [49, 50],  # Don't be afraid
                [51, 52, 53, 54, 55, 56]  # Girl raised
            ],
            9: [
                [1, 2, 3, 4, 5, 6],  # Sending the Twelve
                [7, 8, 9],  # Herod's perplexity
                [10, 11],  # Apostles return
                [12, 13, 14, 15, 16, 17],  # Feeding 5000
                [18, 19, 20, 21, 22],  # Peter's confession and first passion prediction
                [23, 24, 25, 26, 27],  # Take up cross
                [28, 29, 30, 31, 32, 33, 34, 35, 36],  # Transfiguration
                [37, 38, 39, 40, 41, 42, 43],  # Boy with evil spirit
                [43, 44, 45],  # Second passion prediction
                [46, 47, 48],  # Greatest in kingdom
                [49, 50],  # Not against us
                [51, 52, 53],  # Samaritan village
                [54, 55, 56],  # Jesus rebukes disciples
                [57, 58],  # Foxes have holes
                [59, 60],  # Let dead bury dead
                [61, 62]  # No one who puts hand to plow
            ],
            10: [
                [1, 2, 3, 4, 5, 6, 7],  # Sending the seventy-two
                [8, 9, 10, 11, 12],  # Instructions
                [13, 14, 15, 16],  # Woe to unrepentant cities
                [17, 18, 19, 20],  # Return of seventy-two
                [21, 22],  # Jesus rejoices
                [23, 24],  # Blessed are eyes that see
                [25, 26, 27, 28],  # Greatest commandment
                [29, 30, 31, 32, 33, 34, 35, 36, 37],  # Good Samaritan
                [38, 39, 40, 41, 42]  # Mary and Martha
            ],
            11: [
                [1, 2, 3, 4],  # Lord's Prayer
                [5, 6, 7, 8],  # Friend at midnight
                [9, 10, 11, 12, 13],  # Ask, seek, knock
                [14, 15, 16],  # Beelzebul accusation
                [17, 18, 19, 20, 21, 22, 23],  # Kingdom divided
                [24, 25, 26],  # Return of evil spirit
                [27, 28],  # Blessed is the mother
                [29, 30, 31, 32],  # Sign of Jonah
                [33, 34, 35, 36],  # Lamp of the body
                [37, 38, 39, 40, 41],  # Woe to Pharisees (cleanliness)
                [42, 43, 44],  # Woe to Pharisees (tithing, honor, graves)
                [45, 46],  # Woe to lawyers (burdens)
                [47, 48, 49, 50, 51],  # Woe to lawyers (prophets)
                [52, 53, 54]  # Woe to lawyers (knowledge)
            ],
            12: [
                [1, 2, 3],  # Beware the yeast
                [4, 5],  # Fear God
                [6, 7],  # God's care
                [8, 9, 10],  # Acknowledge Christ
                [11, 12],  # Holy Spirit teaches
                [13, 14, 15],  # Rich fool parable intro
                [16, 17, 18, 19, 20, 21],  # Rich fool parable
                [22, 23, 24, 25, 26],  # Do not worry (ravens)
                [27, 28, 29, 30, 31],  # Do not worry (lilies)
                [32, 33, 34],  # Treasures in heaven
                [35, 36, 37, 38],  # Waiting servants
                [39, 40],  # Thief in night
                [41, 42, 43, 44, 45, 46],  # Faithful and wise manager
                [47, 48],  # Servant's beatings
                [49, 50, 51, 52, 53],  # Division, not peace
                [54, 55, 56, 57],  # Interpreting the times
                [58, 59]  # Settle with adversary
            ],
            13: [
                [1, 2, 3, 4, 5],  # Repent or perish
                [6, 7, 8, 9],  # Barren fig tree
                [10, 11, 12, 13],  # Healing on Sabbath
                [14, 15, 16, 17],  # Synagogue leader rebuked
                [18, 19],  # Mustard seed
                [20, 21],  # Yeast
                [22, 23, 24],  # Narrow door
                [25, 26, 27],  # Too late
                [28, 29, 30],  # Last will be first
                [31, 32, 33],  # Herod wants to kill
                [34, 35]  # Lament over Jerusalem
            ],
            14: [
                [1, 2, 3, 4, 5, 6],  # Healing on Sabbath
                [7, 8, 9, 10, 11],  # Parable of wedding feast
                [12, 13, 14],  # Invite the poor
                [15, 16, 17, 18, 19, 20, 21, 22, 23, 24],  # Great banquet
                [25, 26, 27],  # Cost of discipleship
                [28, 29, 30],  # Counting the cost (tower)
                [31, 32, 33],  # Counting the cost (war)
                [34, 35]  # Worthless salt
            ],
            15: [
                [1, 2],  # Tax collectors gather
                [3, 4, 5, 6, 7],  # Lost sheep
                [8, 9, 10],  # Lost coin
                [11, 12, 13, 14, 15, 16],  # Prodigal departs and returns
                [17, 18, 19, 20],  # Prodigal's return
                [21, 22, 23, 24],  # Father's celebration
                [25, 26, 27, 28],  # Older brother
                [29, 30, 31, 32]  # Father's response
            ],
            16: [
                [1, 2, 3, 4, 5, 6, 7, 8],  # Shrewd manager
                [9, 10, 11, 12, 13],  # Faithful in little
                [14, 15],  # Pharisees scoff
                [16, 17, 18],  # Law and Prophets
                [19, 20, 21],  # Rich man and Lazarus intro
                [22, 23, 24, 25, 26],  # After death
                [27, 28, 29, 30, 31]  # Abraham's response
            ],
            17: [
                [1, 2],  # Stumbling blocks
                [3, 4],  # Rebuke and forgive
                [5, 6],  # Increase our faith
                [7, 8, 9, 10],  # Unworthy servants
                [11, 12, 13, 14],  # Ten lepers healed
                [15, 16, 17, 18, 19],  # One returns
                [20, 21],  # Kingdom within
                [22, 23, 24, 25],  # Days of Son of Man
                [26, 27, 28, 29, 30],  # As in days of Noah and Lot
                [31, 32, 33],  # Don't look back
                [34, 35, 36, 37]  # One taken, one left
            ],
            18: [
                [1, 2, 3, 4, 5, 6, 7, 8],  # Persistent widow
                [9, 10, 11, 12, 13, 14],  # Pharisee and tax collector
                [15, 16, 17],  # Little children
                [18, 19, 20, 21, 22, 23],  # Rich young ruler
                [24, 25, 26, 27],  # Hard for rich
                [28, 29, 30],  # Rewards of following
                [31, 32, 33, 34],  # Third passion prediction
                [35, 36, 37, 38, 39],  # Blind beggar calls out
                [40, 41, 42, 43]  # Healing and response
            ],
            19: [
                [1, 2, 3, 4],  # Zacchaeus
                [5, 6, 7],  # Jesus calls him
                [8, 9, 10],  # Salvation comes
                [11, 12, 13, 14, 15],  # Parable of minas intro
                [16, 17, 18, 19],  # First two servants
                [20, 21, 22, 23, 24, 25, 26],  # Third servant
                [27],  # Enemies killed
                [28, 29, 30, 31, 32, 33, 34, 35],  # Triumphal entry preparation
                [36, 37, 38],  # Entry into Jerusalem
                [39, 40],  # Pharisees object
                [41, 42, 43, 44],  # Weeping over Jerusalem
                [45, 46],  # Cleansing temple
                [47, 48]  # Teaching daily
            ],
            20: [
                [1, 2, 3, 4, 5, 6, 7, 8],  # Authority questioned
                [9, 10, 11, 12, 13, 14, 15, 16],  # Parable of tenants
                [17, 18, 19],  # Stone the builders rejected
                [20, 21, 22, 23, 24, 25, 26],  # Taxes to Caesar
                [27, 28, 29, 30, 31, 32, 33],  # Sadducees' question
                [34, 35, 36, 37, 38],  # Jesus's answer
                [39, 40],  # Teachers impressed
                [41, 42, 43, 44],  # Whose son is Christ
                [45, 46, 47]  # Beware the scribes
            ],
            21: [
                [1, 2, 3, 4],  # Widow's offering
                [5, 6],  # Temple destruction predicted
                [7, 8, 9, 10, 11],  # Signs of the end
                [12, 13, 14, 15, 16, 17, 18, 19],  # Persecution
                [20, 21, 22, 23, 24],  # Destruction of Jerusalem
                [25, 26, 27, 28],  # Son of Man coming
                [29, 30, 31],  # Fig tree
                [32, 33],  # This generation
                [34, 35, 36],  # Watch yourselves
                [37, 38]  # Jesus teaching daily
            ],
            22: [
                [1, 2],  # Plot to kill Jesus
                [3, 4, 5, 6],  # Judas agrees to betray
                [7, 8, 9, 10, 11, 12, 13],  # Passover preparation
                [14, 15, 16],  # Passover with disciples
                [17, 18],  # Cup divided
                [19, 20],  # This is my body
                [21, 22, 23],  # Betrayer at table
                [24, 25, 26, 27],  # Greatest among you
                [28, 29, 30],  # Confer kingdom
                [31, 32, 33, 34],  # Peter's denial predicted
                [35, 36, 37, 38],  # Two swords
                [39, 40],  # Mount of Olives
                [41, 42, 43, 44, 45, 46],  # Gethsemane
                [47, 48],  # Betrayal kiss
                [49, 50, 51],  # Disciples strike
                [52, 53],  # Jesus to crowd
                [54, 55, 56, 57, 58],  # Peter's first denial
                [59, 60, 61, 62],  # Peter's other denials
                [63, 64, 65],  # Mocking Jesus
                [66, 67, 68, 69, 70, 71]  # Before Sanhedrin
            ],
            23: [
                [1, 2, 3, 4, 5],  # Before Pilate
                [6, 7],  # Sent to Herod
                [8, 9, 10, 11, 12],  # Before Herod
                [13, 14, 15, 16],  # Pilate finds no guilt
                [17, 18, 19, 20, 21, 22, 23, 24, 25],  # Crowd demands Barabbas
                [26],  # Simon carries cross
                [27, 28, 29, 30, 31],  # Women weep
                [32, 33],  # Crucified with criminals
                [34],  # Father forgive them
                [35, 36, 37],  # Mocking
                [38],  # Inscription
                [39, 40, 41, 42, 43],  # Criminals
                [44, 45],  # Darkness
                [46],  # Jesus dies
                [47, 48, 49],  # Responses to death
                [50, 51, 52, 53],  # Joseph buries Jesus
                [54, 55, 56]  # Women prepare spices
            ],
            24: [
                [1, 2, 3],  # Empty tomb
                [4, 5, 6, 7],  # Angels speak
                [8, 9, 10, 11, 12],  # Women tell apostles
                [13, 14, 15, 16, 17],  # Road to Emmaus
                [18, 19, 20, 21],  # Events in Jerusalem
                [22, 23, 24],  # Empty tomb report
                [25, 26, 27],  # Jesus explains
                [28, 29],  # Stay with us
                [30, 31, 32],  # Breaking bread
                [33, 34, 35],  # Return to Jerusalem
                [36, 37, 38, 39, 40, 41, 42, 43],  # Jesus appears
                [44, 45, 46, 47, 48, 49],  # Jesus teaches
                [50, 51],  # Ascension
                [52, 53]  # Disciples worship
            ]
        }
    }
}

def download_bsb():
    """Download the BSB text."""
    url = 'https://bereanbible.com/bsb.txt'
    print('Downloading BSB...')
    with urllib.request.urlopen(url) as response:
        return response.read().decode('utf-8')

def extract_book(bsb_text, book_config):
    """Extract a specific book from BSB text."""
    lines = bsb_text.split('\n')
    book_lines = []
    in_book = False

    for line in lines:
        # Check for start of book
        if re.match(book_config['start_pattern'], line):
            in_book = True
        # Check for end of book
        elif re.match(book_config['end_pattern'], line):
            in_book = False

        if in_book and line.strip():
            book_lines.append(line)

    return book_lines

def parse_verses(book_lines):
    """Parse verse text into structured data."""
    chapters = {}

    for line in book_lines:
        # Match pattern like "Mark 1:1 text here"
        match = re.match(r'^[A-Za-z\s]+(\d+):(\d+)\s+(.+)$', line)
        if match:
            chapter_num = int(match.group(1))
            verse_num = int(match.group(2))
            text = match.group(3)

            if chapter_num not in chapters:
                chapters[chapter_num] = {}

            chapters[chapter_num][verse_num] = text

    return chapters

def is_in_open_dialogue(text):
    """Check if text ends with an open quotation (odd number of quotes)."""
    # Count quotation marks in the text (both straight and curly quotes)
    straight_quotes = text.count('"')
    curly_open = text.count('“')
    curly_close = text.count('”')

    # For curly quotes, check if there are more opening than closing
    if curly_open > 0 or curly_close > 0:
        return curly_open > curly_close

    # For straight quotes, check if odd number
    return straight_quotes % 2 == 1

def add_continuation_quotes(paragraphs):
    """Add opening quotes to paragraphs that continue dialogue."""
    global in_dialogue

    for para_idx, paragraph in enumerate(paragraphs):
        if not paragraph:
            continue

        # If we're in ongoing dialogue and this paragraph doesn't start with a quote,
        # add one to indicate continuation
        first_verse_text = paragraph[0]['text']
        if in_dialogue and not first_verse_text.startswith(('"', '“')):
            paragraph[0]['text'] = '“' + first_verse_text

        # Check the last verse of this paragraph to see if dialogue is still open
        last_verse_text = paragraph[-1]['text']
        in_dialogue = is_in_open_dialogue(last_verse_text)

    return paragraphs

def create_paragraph_structure(chapters, paragraph_structure):
    """Create paragraph structure from verse data."""
    result = []

    for chapter_num in sorted(chapters.keys()):
        chapter_verses = chapters[chapter_num]

        if paragraph_structure and chapter_num in paragraph_structure:
            # Use manual paragraph structure
            paragraphs = []
            for verse_group in paragraph_structure[chapter_num]:
                paragraph = []
                for verse_num in verse_group:
                    if verse_num in chapter_verses:
                        paragraph.append({
                            'number': verse_num,
                            'text': chapter_verses[verse_num]
                        })
                if paragraph:
                    paragraphs.append(paragraph)

            # Add continuation quotes for dialogue
            paragraphs = add_continuation_quotes(paragraphs)
        else:
            # Default: each verse is its own paragraph
            paragraphs = [[{'number': v, 'text': chapter_verses[v]}]
                         for v in sorted(chapter_verses.keys())]

        result.append({
            'chapter': chapter_num,
            'paragraphs': paragraphs
        })

    return result

def generate_js_file(book_data, output_file):
    """Generate JavaScript data file."""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f'// Berean Standard Bible\n')
        f.write('const bookData = ')
        json.dump(book_data, f, indent=2, ensure_ascii=False)
        f.write(';\n')

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 parse_bsb_book.py <book_id>")
        print(f"Available books: {', '.join(BOOK_CONFIGS.keys())}")
        sys.exit(1)

    book_id = sys.argv[1].lower()

    if book_id not in BOOK_CONFIGS:
        print(f"Unknown book: {book_id}")
        print(f"Available books: {', '.join(BOOK_CONFIGS.keys())}")
        sys.exit(1)

    config = BOOK_CONFIGS[book_id]

    # Warn if paragraph structure is not defined
    if config['paragraph_structure'] is None:
        print(f"Warning: No paragraph structure defined for {config['full_name']}")
        print("Using default structure (one paragraph per verse)")
        print()

    # Download and parse
    bsb_text = download_bsb()
    book_lines = extract_book(bsb_text, config)
    print(f"Extracted {len(book_lines)} lines from {config['full_name']}")

    chapters = parse_verses(book_lines)
    print(f"Parsed {len(chapters)} chapters")

    book_data = create_paragraph_structure(chapters, config['paragraph_structure'])

    # Generate output file
    output_file = f'data-{book_id}.js'
    generate_js_file(book_data, output_file)
    print(f"Generated {output_file}")

    # Print summary
    total_verses = sum(len(ch['paragraphs']) if config['paragraph_structure'] is None
                      else sum(len(p) for p in ch['paragraphs'])
                      for ch in book_data)
    total_paragraphs = sum(len(ch['paragraphs']) for ch in book_data)
    print(f"Total verses: {total_verses}")
    print(f"Total paragraphs: {total_paragraphs}")

if __name__ == '__main__':
    main()
