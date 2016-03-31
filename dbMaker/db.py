import sqlite3

class DBInterface():
    
    def __init__(self, fname="main.db"):
        self.connection = sqlite3.connect(fname)
        self.cursor = self.connection.cursor()
        self.key_types = [
                ("sample_id", "INTEGER PRIMARY KEY"),
                ("sample_type", "VARCHAR(20)"),
                ("twiki_name", "VARCHAR(50)"),
                ("dataset_name", "VARCHAR(250)"),
                ("location", "VARCHAR(300)"),
                ("filter_type", "VARCHAR(20)"),
                ("nevents_in", "INTEGER"),
                ("nevents_out", "INTEGER"),
                ("filter_eff", "FLOAT"),
                ("xsec", "FLOAT"),
                ("kfactor", "FLOAT"),
                ("gtag", "VARCHAR(40)"),
                ("cms3tag", "VARCHAR(20)"),
                ("assigned_to", "VARCHAR(20)"),
                ("comments", "VARCHAR(100)"),
                ]

    def drop_table(self):
        self.cursor.execute("drop table if exists sample")

    def make_table(self):
        sql_cmd = "CREATE TABLE sample (%s)" % ",".join(["%s %s" % (key, typ) for (key, typ) in self.key_types])
        self.cursor.execute(sql_cmd)

    # import time    
    # print time.strftime('%Y-%m-%d %H:%M:%S')

    def make_val_str(self, vals):
        return map(lambda x: '"%s"' % x if type(x) in [str,unicode] else str(x), vals)

    def do_insert_dict(self, d):
        # provide a dict to insert into the table
        keys, vals = zip(*d.items())
        key_str = ",".join(keys)
        val_str = ",".join(self.make_val_str(vals))
        sql_cmd = "insert into sample (%s) values (%s);" % (key_str, val_str)
        self.cursor.execute(sql_cmd)

    def do_update_dict(self, d, idx):
        # provide a dict and index to update
        keys, vals = zip(*d.items())
        val_strs = self.make_val_str(vals)
        set_str = ",".join(map(lambda (x,y): "%s=%s" % (x,y), zip(keys, val_strs)))
        sql_cmd = "update sample set %s where sample_id=%i" % (set_str, idx)
        self.cursor.execute(sql_cmd)

    def is_already_in_table(self, d):
        # provide a dict and this will use appropriate keys to see if it's already in the database
        # this returns an ID (non-zero int) corresponding to the row matching the dict
        dataset_name, sample_type, cms3tag, location = d.get("dataset_name",""), d.get("sample_type",""), d.get("cms3tag",""), d.get("location","")
        sql_cmd = "select sample_id from sample where dataset_name=? and sample_type=? and cms3tag=? and location=? limit 1"
        self.cursor.execute(sql_cmd, (dataset_name, sample_type, cms3tag, location))
        return self.cursor.fetchone()

    def read_to_dict_list(self, query):
        # return list of sample dictionaries
        self.cursor.execute(query)
        col_names = [e[0] for e in self.cursor.description]
        self.cursor.execute(query)
        toreturn = []
        for r in self.cursor.fetchall():
            toreturn.append( dict(zip(col_names, r)) )
        return toreturn

    def update_sample(self, d):
        # provide dictionary, and this will update sample if it already exists, or insert it

        if not d: return False
        if self.unknown_keys(d): return False

        # totally ignore the sample_id
        if "sample_id" in d: del d["sample_id"]
        already_in = self.is_already_in_table(d)
        if already_in: self.do_update_dict(d, already_in[0])
        else: self.do_insert_dict(d)
        self.connection.commit()
        return True

    def fetch_samples_matching(self, d):
        # provide dictionary and this will find samples with matching key-value pairs

        if not d: return []
        if self.unknown_keys(d): return []

        keys, vals = zip(*d.items())
        val_strs = self.make_val_str(vals)
        set_str = " and ".join(map(lambda (x,y): "%s=%s" % (x,y), zip(keys, val_strs)))
        sql_cmd = "select * from sample where %s" % (set_str)
        return self.read_to_dict_list(sql_cmd)

    def unknown_keys(self, d):
        # returns True if there are unrecognized keys
        unknown_keys = list(set(d.keys()) - set([kt[0] for kt in self.key_types]))
        if len(unknown_keys) > 0:
            # print "I don't recognize the keys: %s" % ", ".join(unknown_keys)
            return True
        else: return False


    def close(self):
        self.connection.close()


if __name__=='__main__':
    import tester
    if tester.do_test():
        print "Calculations correct"

