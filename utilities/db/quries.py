from utilities.db.db_manager import dbManager, DBManager


class DBQuery:

    def _init_(self):
        """
        Init dbmanager
        """
        self.db = DBManager()

    ## User queries
    def set_new_user(self, email, fname, lname, password, bd, city, pic):
        self.db = DBManager()
        row = self.db.commit(
            "insert into users(email, first_name, last_name, password, birth_date, city, profile_pic) values ('%s', '%s', '%s', '%s', '%s', '%s', '%s' )" %
            (email, fname, lname, password, bd, city, pic))
        return row

    def get_user(self, email, password):
        self.db = DBManager()
        user = self.db.fetch(
            "select * from users where email='%s' and password='%s'" % (email, password))
        return user

    def get_user_vote_details_discussion(self, disc_id, email):
        self.db = DBManager()
        vote_details = self.db.fetch(
            "select * from user_vote_disc where discussion_id='%s' and voter='%s'" % (disc_id, email))
        return vote_details

    def get_user_details(self, email):
        self.db = DBManager()
        user = self.db.fetch(
            "select * from users where email='%s' " % email)
        return user

    ## Discussions queries
    def get_max_id_discuss(self):
        self.db = DBManager()
        max_id = self.db.fetch(
            "select (max(discussion_id)+1) as max_discuss from discussions")
        max_id = max_id[0].max_discuss
        return max_id

    def insert_discuss(self, discussion_id, title, description, due_date, email):
        self.db = DBManager()
        query = "insert into discussions(discussion_id, title, description, due_date, discussion_owner) values  ('%s','%s','%s','%s','%s')" % (
            discussion_id, title, description, due_date, email)
        user = self.db.commit(query=query)
        self.insert_node_question(discussion_id, title, email, description)
        return user

    def get_all_discussions(self):
        self.db = DBManager()
        query = "SELECT discussion_id,title,description,due_date,discussion_owner,date_format(creation_date,'%Y-%m-%d %H:%i') as creation_date,status,u.first_name,u.last_name FROM discussions as d join users as u on d.discussion_owner = u.email"
        res = self.db.fetch(query=query)
        return res

    def get_all_discussions_of_a_user(self, email):
        self.db = DBManager()
        query = "SELECT * FROM discussions where discussion_owner = '%s'" % email
        res = self.db.fetch(query=query)
        return res

    def get_all_favorites_discussions_of_a_user(self, email):
        self.db = DBManager()
        query = "SELECT d.* FROM discussions as d join favorites as f on d.discussion_id =f.discussion_id where discussion_owner = '%s'" % email
        res = self.db.fetch(query=query)
        return res

    ## Favorties queries
    def insert_favorite(self, email, discussion_id):
        self.db = DBManager()
        query = "insert into favorites(email, discussion_id ) values  ('%s','%s')" % (email, discussion_id)
        res = self.db.commit(query=query)
        return res

    def delete_favorite(self, email, discussion_id):
        self.db = DBManager()
        query = "Delete from favorites where email = '%s' and discussion_id = '%s'" % (email, discussion_id)
        res = self.db.commit(query=query)
        return res

    def get_favorites(self, email):
        self.db = DBManager()
        query = "SELECT discussion_id FROM favorites where email = '%s'" % email
        res = self.db.fetch(query=query)
        return res

    ## discussion page queries
    ## for info section:
    def get_discussions_by_id(self, discussion_id):
        self.db = DBManager()
        query = "SELECT * FROM discussions as d join users as u on d.discussion_owner = u.email where discussion_id = '%s'" % discussion_id
        res = self.db.fetch(query=query)
        return res

    ## for comments list section:
    def get_all_comments_list(self, discussion_id):
        self.db = DBManager()
        query = "select * from nodes as n join users as u on n.node_owner = u.email where discussion_id = '%s' " % discussion_id
        res = self.db.fetch(query=query)
        return res

        ## for merge list section:

    def get_merge_list(self, discussion_id):
        self.db = DBManager()
        query = "select node_content from nodes where discussion_id = '%s' " % discussion_id
        res = self.db.fetch(query=query)
        return res

    def insert_node_question(self, discussion_id, title, email, description):
        self.db = DBManager()
        query = "insert into nodes (discussion_id, node_content, node_owner, node_level, node_description) values ('%s', '%s', '%s',0,'%s')" % (
            discussion_id, title, email, description)
        res = self.db.commit(query=query)
        return res

    def insert_node_comment(self, discussion_id, parent_node, title, email, node_level, description):
        self.db = DBManager()
        query = "insert into nodes (discussion_id, parent_node, node_content, node_owner, node_level,node_description) values ('%s', '%s', '%s', '%s', '%s','%s')" % (
            discussion_id, parent_node, title, email, node_level, description)
        res = self.db.commit(query=query)
        return res

    def get_node_id_level(self, node_id):
        self.db = DBManager()
        query = "select (node_level) from nodes where node_id = '%s' " % node_id
        res = self.db.fetch(query=query)
        res = res[0].node_level
        return res

    ## for votings:
    def vote_for_comment(self, email, discussion_id, node_id, amount, first_time, last_time):
        self.db = DBManager()
        query1 = "select score from user_vote_disc where voter='%s' and discussion_id='%s' " % (email, discussion_id)
        res1 = self.db.fetch(query=query1)
        res1 = int(res1[0].score)
        query2 = "select node_score from nodes where node_id='%s'" % node_id
        res2 = self.db.fetch(query=query2)
        res2 = int(res2[0].node_score)
        amount = int(amount)
        if res1 >= amount:
            if first_time == 1:
                update_user_tokens = "update user_vote_disc set score = '%s' where voter='%s' and discussion_id='%s' " % (
                    res1 - amount, email, discussion_id)
                self.db.commit(query=update_user_tokens)
            if last_time == 1:
                update_node_score = "update nodes set node_score = '%s' where node_id='%s'" % (res2 + amount, node_id)
                self.db.commit(query=update_node_score)
            return True
        else:
            return False

    def rank_final_decision(self, email, discussion_id, node_id, amount):
        self.db = DBManager()
        query1 = "select score from user_vote_disc where voter='%s' and discussion_id='%s' " % (email, discussion_id)
        res1 = self.db.fetch(query=query1)
        res1 = int(res1[0].score)
        query2 = "select node_score from nodes where node_id='%s'" % node_id
        res2 = self.db.fetch(query=query2)
        res2 = int(res2[0].node_score)
        amount = int(amount)
        if res1 >= amount:
            update_user_tokens = "update user_vote_disc set score = '%s' where voter='%s' and discussion_id='%s' " % (
                res1 - amount, email, discussion_id)
            self.db.commit(query=update_user_tokens)
            update_node_score = "update nodes set node_score = '%s' where node_id='%s'" % (res2 + amount, node_id)
            self.db.commit(query=update_node_score)

    def rank_final_decision_new(self, email, discussion_id, node_id, amount):
        self.db = DBManager()
        query1 = "select score from user_vote_disc where voter='%s' and discussion_id='%s' " % (email, discussion_id)
        res1 = self.db.fetch(query=query1)
        res1 = int(res1[0].score)
        query2 = "select node_score from nodes where node_id='%s'" % node_id
        res2 = self.db.fetch(query=query2)
        res2 = int(res2[0].node_score)
        amount = int(amount)
        if res1 >= amount:
            update_user_tokens = "update user_vote_disc set score = '%s' where voter='%s' and discussion_id='%s' " % (
                res1 - amount, email, discussion_id)
            self.db.commit(query=update_user_tokens)
            update_node_score = "update nodes set node_score = '%s' where node_id='%s'" % (res2 + amount, node_id)
            self.db.commit(query=update_node_score)

    def delete_min_rank(self, node_id):
        self.db = DBManager()
        print(' i am in qureis.py')
        print(node_id)
        query = "delete from nodes where node_id='%s'" % node_id
        self.db.commit(query=query)

    def update_discussion_status(self, dis_id, status):
        self.db = DBManager()
        update_status = "update discussions set status = '%s' where discussion_id='%s'" % (status, dis_id)
        self.db.commit(query=update_status)

    def reset_ranking(self, dis_id):
        self.db = DBManager()
        update_ranking = "update nodes set node_score = 0 where discussion_id='%s'" % dis_id
        self.db.commit(query=update_ranking)

    def set_default_user_tokens(self, dis_id):
        self.db = DBManager()
        update_tokens = "update user_vote_disc set score = 100 where discussion_id='%s'" % dis_id
        self.db.commit(query=update_tokens)

    def get_parent_id(self, node_id):
        self.db = DBManager()
        query = "select (parent_node), node_content from nodes where node_id = '%s' " % node_id
        res = self.db.fetch(query=query)
        res1 = res[0].parent_node
        res2 = res[0].node_content
        return res1, res2

    def get_level_parent(self, node_id):
        self.db = DBManager()
        parent_level = "select parent_node from nodes where node_id = '%s' " % node_id
        res = self.db.fetch(query=parent_level)
        if res[0].parent_node is None:
            res = 0
            flag = 1
        else:
            res = res[0].parent_node
            flag = 0
        if res is not None and flag == 0:
            query = "select node_level from nodes where node_id = '%s' " % res
            res = self.db.fetch(query=query)
            res = res[0].node_level
        else:
            res = 0
        return res

    def initial_score_for_discussion(self, discussion_id, email):
        self.db = DBManager()
        query = "insert into user_vote_disc(voter, discussion_id) values ('%s', '%s')" % (
            email, discussion_id)
        res = self.db.commit(query=query)
        return res

    def check_if_joined(self, discussion_id, email):
        self.db = DBManager()
        query = "select * from user_vote_disc where voter='%s' and discussion_id='%s' " % (
            email, discussion_id)
        res = self.db.fetch(query=query)
        if len(res):
            res = True
        else:
            res = False
        print(res)
        return res

    def get_top_decisions(self, discussion_id, top_number):
        self.db = DBManager()
        query = "SELECT node_content, node_score, node_owner, node_id FROM nodes where discussion_id = '%s' order by node_score desc limit %s" % (
            discussion_id, top_number)
        res = self.db.fetch(query=query)
        return res

    def update_num_comments_user(self, email):
        self.db = DBManager()
        query = "UPDATE users set comments_num = comments_num+1 where email = '%s'" % email
        res = self.db.commit(query=query)
        return res

    def update_num_final_des_user(self, email):
        self.db = DBManager()
        query = "UPDATE users set final_dec_num = final_dec_num+1 where email = '%s'" % email
        res = self.db.commit(query=query)
        return res

    def insert_image(self, pic, email):
        self.db = DBManager()
        query = "insert into users (profile_pic) value '%s' where email = '%s'" % (pic, email)
        res = self.db.commit(query=query)
        return res

    def update_level(self, email, level):
        self.db = DBManager()
        level = str(level)
        query = "update users set user_rank = '%s' where email = '%s'" % (level, email)
        res = self.db.commit(query=query)
        return res

    def join_discussion(self, email, discussion_id):
        self.db = DBManager()
        query = "insert into user_vote_disc  values('%s','%s',100)" % (email, discussion_id)
        res = self.db.commit(query=query)
        return res

    def raise_comment_level(self, content, owner, description, node_id):
        self.db = DBManager()
        query = "update nodes set node_content = '%s', node_owner='%s',node_description='%s' where node_id = '%s'" % (
        content, owner, description, node_id)
        res = self.db.commit(query=query)
        return res

    def get_parent_score(self, node_id):
        self.db = DBManager()
        query = "select node_score from nodes where node_id = %s" % node_id
        res = self.db.fetch(query=query)
        res1 = res[0].node_score
        return res1

    def update_top_num_final(self, discussion_id, top_number):
        self.db = DBManager()
        query = "update discussions set top_num_for_final = %s where discussion_id = %s" % (top_number,discussion_id )
        res = self.db.commit(query=query)
        return res

    def get_top_final(self, discussion_id):
        self.db = DBManager()
        query = "select top_num_for_final from discussions where discussion_id = %s" % discussion_id
        res = self.db.fetch(query=query)
        res1 = res[0].top_num_for_final
        return res1

