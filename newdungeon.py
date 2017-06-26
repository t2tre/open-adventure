#!/usr/bin/python3

# This is the new open-adventure dungeon generator. It'll eventually
# replace the existing dungeon.c It currently outputs a .h and .c pair
# for C code.

import yaml

yaml_name = "adventure.yaml"
h_name = "newdb.h"
c_name = "newdb.c"

statedefines = ""

h_template = """/* Generated from adventure.yaml - do not hand-hack! */
#ifndef NEWDB_H
#define NEWDB_H

#include <stdio.h>
#include <stdbool.h>

#define SILENT	-1	/* no sound */

/* Symbols for cond bits */
#define COND_LIT	0	/* Light */
#define COND_OILY	1	/* If bit 2 is on: on for oil, off for water */
#define COND_FLUID	2	/* Liquid asset, see bit 1 */
#define COND_NOARRR	3	/* Pirate doesn't go here unless following */
#define COND_NOBACK	4	/* Cannot use "back" to move away */
#define COND_ABOVE	5
#define COND_DEEP	6	/* Deep - e.g where dwarves are active */
#define COND_FOREST	7	/* In the forest */
#define COND_FORCED	8	/* Only one way in or out of here */
/* Bits past 10 indicate areas of interest to "hint" routines */
#define COND_HBASE	10	/* Base for location hint bits */
#define COND_HCAVE	11	/* Trying to get into cave */
#define COND_HBIRD	12	/* Trying to catch bird */
#define COND_HSNAKE	13	/* Trying to deal with snake */
#define COND_HMAZE	14	/* Lost in maze */
#define COND_HDARK	15	/* Pondering dark room */
#define COND_HWITT	16	/* At Witt's End */
#define COND_HCLIFF	17	/* Cliff with urn */
#define COND_HWOODS	18	/* Lost in forest */
#define COND_HOGRE	19	/* Trying to deal with ogre */
#define COND_HJADE	20	/* Found all treasures except jade */

typedef struct {{
  const char* inventory;
  int plac, fixd;
  bool is_treasure;
  const char** longs;
  const char** sounds;
  const char** texts;
}} object_description_t;

typedef struct {{
  const char* small;
  const char* big;
}} descriptions_t;

typedef struct {{
  descriptions_t description;
  const long sound;
  const bool loud;
}} location_t;

typedef struct {{
  const char* query;
  const char* yes_response;
}} obituary_t;

typedef struct {{
  const int threshold;
  const int point_loss;
  const char* message;
}} turn_threshold_t;

typedef struct {{
  const int threshold;
  const char* message;
}} class_t;

typedef struct {{
  const int number;
  const int turns;
  const int penalty;
  const char* question;
  const char* hint;
}} hint_t;

typedef struct {{
  const char* word;
  const int type;
  const int value;
}} vocabulary_t;

extern const location_t locations[];
extern const object_description_t object_descriptions[];
extern const char* arbitrary_messages[];
extern const class_t classes[];
extern const turn_threshold_t turn_thresholds[];
extern const obituary_t obituaries[];
extern const hint_t hints[];
extern long conditions[];
extern const vocabulary_t vocabulary[];
extern const long actspk[];

#define NLOCATIONS	{}
#define NOBJECTS	{}
#define NHINTS		{}
#define NCLASSES	{}
#define NDEATHS		{}
#define NTHRESHOLDS	{}
#define NVERBS  	{}

enum arbitrary_messages_refs {{
{}
}};

enum locations_refs {{
{}
}};

enum object_descriptions_refs {{
{}
}};

/* State definitions */

{}
#endif /* end NEWDB_H */
"""

c_template = """/* Generated from adventure.yaml - do not hand-hack! */

#include "common.h"
#include "{}"

const char* arbitrary_messages[] = {{
{}
}};

const class_t classes[] = {{
{}
}};

const turn_threshold_t turn_thresholds[] = {{
{}
}};

const location_t locations[] = {{
{}
}};

const object_description_t object_descriptions[] = {{
{}
}};

const obituary_t obituaries[] = {{
{}
}};

const hint_t hints[] = {{
{}
}};

long conditions[] = {{
{}
}};

const vocabulary_t vocabulary[] = {{
{}
}};

const long actspk[] = {{
    NO_MESSAGE,
{}
}};

/* end */
"""

def make_c_string(string):
    """Render a Python string into C string literal format."""
    if string == None:
        return "NULL"
    string = string.replace("\n", "\\n")
    string = string.replace("\t", "\\t")
    string = string.replace('"', '\\"')
    string = string.replace("'", "\\'")
    string = '"' + string + '"'
    return string

def get_refs(l):
    reflist = [x[0] for x in l]
    ref_str = ""
    for ref in reflist:
        ref_str += "    {},\n".format(ref)
    ref_str = ref_str[:-1] # trim trailing newline
    return ref_str

def get_arbitrary_messages(arb):
    template = """    {},
"""
    arb_str = ""
    for item in arb:
        arb_str += template.format(make_c_string(item[1]))
    arb_str = arb_str[:-1] # trim trailing newline
    return arb_str

def get_class_messages(cls):
    template = """    {{
        .threshold = {},
        .message = {},
    }},
"""
    cls_str = ""
    for item in cls:
        threshold = item["threshold"]
        message = make_c_string(item["message"])
        cls_str += template.format(threshold, message)
    cls_str = cls_str[:-1] # trim trailing newline
    return cls_str

def get_turn_thresholds(trn):
    template = """    {{
        .threshold = {},
        .point_loss = {},
        .message = {},
    }},
"""
    trn_str = ""
    for item in trn:
        threshold = item["threshold"]
        point_loss = item["point_loss"]
        message = make_c_string(item["message"])
        trn_str += template.format(threshold, point_loss, message)
    trn_str = trn_str[:-1] # trim trailing newline
    return trn_str

def get_locations(loc):
    template = """    {{ // {}
        .description = {{
            .small = {},
            .big = {},
        }},
        .sound = {},
        .loud = {},
    }},
"""
    loc_str = ""
    for (i, item) in enumerate(loc):
        short_d = make_c_string(item[1]["description"]["short"])
        long_d = make_c_string(item[1]["description"]["long"])
        sound = item[1].get("sound", "SILENT")
        loud = "true" if item[1].get("loud") else "false"
        loc_str += template.format(i, short_d, long_d, sound, loud)
    loc_str = loc_str[:-1] # trim trailing newline
    return loc_str

def get_object_descriptions(obj):
    template = """    {{ // {}
        .inventory = {},
        .plac = {},
        .fixd = {},
        .is_treasure = {},
        .longs = (const char* []) {{
{}
        }},
        .sounds = (const char* []) {{
{}
        }},
        .texts = (const char* []) {{
{}
        }},
    }},
"""
    obj_str = ""
    for (i, item) in enumerate(obj):
        attr = item[1]
        i_msg = make_c_string(attr["inventory"])
        longs_str = ""
        if attr["longs"] == None:
            longs_str = " " * 12 + "NULL,"
        else:
            labels = []
            for l_msg in attr["longs"]:
                if not isinstance(l_msg, str):
                    labels.append(l_msg)
                    l_msg = l_msg[1]
                longs_str += " " * 12 + make_c_string(l_msg) + ",\n"
            longs_str = longs_str[:-1] # trim trailing newline
            if labels:
                global statedefines
                statedefines += "/* States for %s */\n" % item[0]
                for (i, (label, message)) in enumerate(labels):
                    if len(message) >= 45:
                        message = message[:45] + "..."
                    statedefines += "#define %s\t%d /* %s */\n" % (label, i, message)
                statedefines += "\n"
        sounds_str = ""
        if attr.get("sounds") == None:
            sounds_str = " " * 12 + "NULL,"
        else:
             for l_msg in attr["sounds"]:
                 sounds_str += " " * 12 + make_c_string(l_msg) + ",\n"
             sounds_str = sounds_str[:-1] # trim trailing newline
        texts_str = ""
        if attr.get("texts") == None:
            texts_str = " " * 12 + "NULL,"
        else:
             for l_msg in attr["texts"]:
                 texts_str += " " * 12 + make_c_string(l_msg) + ",\n"
             texts_str = texts_str[:-1] # trim trailing newline
        locs = attr.get("locations", ["LOC_NOWHERE", "LOC_NOWHERE"])
        immovable = attr.get("immovable", False)
        try:
            if type(locs) == str:
                locs = [locnames.index(locs), -1 if immovable else 0]
            else:
                locs = [locnames.index(x) for x in locs]
        except IndexError:
            sys.stderr.write("dungeon: unknown object location in %s\n" % locs)
            sys.exit(1)
        treasure = "true" if attr.get("treasure") else "false"
        obj_str += template.format(i, i_msg, locs[0], locs[1], treasure, longs_str, sounds_str, texts_str)
    obj_str = obj_str[:-1] # trim trailing newline
    return obj_str

def get_obituaries(obit):
    template = """    {{
        .query = {},
        .yes_response = {},
    }},
"""
    obit_str = ""
    for o in obit:
        query = make_c_string(o["query"])
        yes = make_c_string(o["yes_response"])
        obit_str += template.format(query, yes)
    obit_str = obit_str[:-1] # trim trailing newline
    return obit_str

def get_hints(hnt, arb):
    template = """    {{
        .number = {},
        .penalty = {},
        .turns = {},
        .question = {},
        .hint = {},
    }},
"""
    hnt_str = ""
    md = dict(arb)
    for member in hnt:
        item = member["hint"]
        number = item["number"]
        penalty = item["penalty"]
        turns = item["turns"]
        question = make_c_string(item["question"])
        hint = make_c_string(item["hint"])
        hnt_str += template.format(number, penalty, turns, question, hint)
    hnt_str = hnt_str[:-1] # trim trailing newline
    return hnt_str

def get_condbits(locations):
    cnd_str = ""
    for (name, loc) in locations:
        conditions = loc["conditions"]
        hints = loc.get("hints") or []
        flaglist = []
        for flag in conditions:
            if conditions[flag]:
                flaglist.append(flag)
        line = "|".join([("(1<<COND_%s)" % f) for f in flaglist])
        trail = "|".join([("(1<<COND_H%s)" % f['name']) for f in hints])
        if trail:
            line += "|" + trail
        if line.startswith("|"):
            line = line[1:]
        if not line:
            line = "0"
        cnd_str += "    " + line + ",\t// " + name + "\n"
    return cnd_str

def recompose(type_word, value):
    "Compose the internal code for a vocabulary word from its YAML entry"
    parts = ("motion", "action", "object", "special")
    try:
        return value + 1000 * parts.index(type_word)
    except KeyError:
        sys.stderr.write("dungeon: %s is not a known word\n" % word)
        sys.exit(1)
    except IndexError:
        sys.stderr.write("%s is not a known word classifier" % attrs["type"])
        sys.exit(1)

def get_vocabulary(vocabulary):
    template = """    {{
        .word = {},
        .type = {},
        .value = {},
    }},
"""
    voc_str = ""
    for vocab in vocabulary:
        word = make_c_string(vocab["word"])
        type_code = recompose(vocab["type"], vocab["value"])
        value = vocab["value"]
        voc_str += template.format(word, type_code, value)
    voc_str = voc_str[:-1] # trim trailing newline
    return voc_str

def get_actspk(actspk):
    res = ""
    for (i, word) in actspk.items():
        res += "    %s,\n" % word
    return res

if __name__ == "__main__":
    with open(yaml_name, "r") as f:
        db = yaml.load(f)

    locnames = [x[0] for x in db["locations"]]

    c = c_template.format(
        h_name,
        get_arbitrary_messages(db["arbitrary_messages"]),
        get_class_messages(db["classes"]),
        get_turn_thresholds(db["turn_thresholds"]),
        get_locations(db["locations"]),
        get_object_descriptions(db["object_descriptions"]),
        get_obituaries(db["obituaries"]),
        get_hints(db["hints"], db["arbitrary_messages"]),
        get_condbits(db["locations"]),
        get_vocabulary(db["vocabulary"]),
        get_actspk(db["actspk"]),
    )

    h = h_template.format(
        len(db["locations"])-1,
        len(db["object_descriptions"])-1,
        len(db["hints"]),
        len(db["classes"]),
        len(db["obituaries"]),
        len(db["turn_thresholds"]),
        len(db["actspk"]),
        get_refs(db["arbitrary_messages"]),
        get_refs(db["locations"]),
        get_refs(db["object_descriptions"]),
        statedefines,
    )

    with open(h_name, "w") as hf:
        hf.write(h)

    with open(c_name, "w") as cf:
        cf.write(c)

# end
