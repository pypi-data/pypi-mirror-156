import tornado.escape
import tornado.ioloop
import tornado.web
from . import worker
from . import util
import threading
from abc import ABCMeta
import logging
import asyncio
import numpy as np
import pandas as pd
import tornado.httpserver
import tornado.netutil
import tornado.websocket
from tornado_swagger.components import components
from tornado_swagger.setup import setup_swagger
import re
import json

l = logging.getLogger("pandem-api")


class apiREST(worker.Worker):
    __metaclass__ = ABCMeta 

    def __init__ (self, name, orchestrator_ref, settings):
        super().__init__(name = name, orchestrator_ref = orchestrator_ref, settings = settings)
        self._api_port = settings["pandem"]["source"]["api"]["port"]
    
    def on_start(self):
        super().on_start()
        self._storage_proxy = self._orchestrator_proxy.get_actor('storage').get().proxy()
        self._variables_proxy = self._orchestrator_proxy.get_actor('variables').get().proxy()
        self._pipeline_proxy = self._orchestrator_proxy.get_actor('pipeline').get().proxy()
        try:
            l.debug("Starting HTTP server")
            sockets = tornado.netutil.bind_sockets(self._api_port) 
            self.server = HttpServer(
                storage_proxy=self._storage_proxy,
                variables_proxy = self._variables_proxy,
                pipeline_proxy = self._pipeline_proxy,
                sockets=sockets
            )
            self.server.start()
        except OSError as err:
            l.debug(f"HTTP server startup failed: {err}")

    def on_stop(self):
        self.server.stop()


class HttpServer(threading.Thread):

    def __init__(self, storage_proxy, variables_proxy, pipeline_proxy, sockets): 
        super().__init__()
        self.storage_proxy = storage_proxy
        self.variables_proxy = variables_proxy
        self.pipeline_proxy = pipeline_proxy
        self.sockets = sockets
        self.app = None
        self.server = None
        self.io_loop = None

    def run(self):
        if asyncio:
            # If asyncio is available, Tornado uses it as its IO loop. Since we
            # start Tornado in a another thread than the main thread, we must
            # explicitly create an asyncio loop for the current thread.
            asyncio.set_event_loop(asyncio.new_event_loop())
        self.app = Application(self.storage_proxy, self.variables_proxy, self.pipeline_proxy)
        self.server = tornado.httpserver.HTTPServer(self.app)
        self.server.add_sockets(self.sockets)
        self.io_loop = tornado.ioloop.IOLoop.current()
        self.io_loop.start()

    def stop(self):
        l.debug("Stopping HTTP server")
        self.io_loop.add_callback(self.io_loop.stop)


class SourcesHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy):
        self.storage_proxy = storage_proxy
    def get(self):
        """
        ---
        tags:
          - Sources
        summary: List sources
        description: List all sources in sources pickle file within the database.
        operationId: getSources
        responses:
            '200':
              description: List all sources including id, name, last and next execution, current status and step of last job and number of issues of last
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/SourcesModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/SourcesModel'
                text/plain:
                  schema:
                    type: string
        """
        df_sources = self.storage_proxy.read_db('source').get()
        df_jobs = self.storage_proxy.read_db('job').get()
        df_issues = self.storage_proxy.read_db('issue').get()
        tags = {}
        sources = {s['name']:s for s in (df_sources.to_dict('records') if df_sources is not None else [])} 
        jobs = df_jobs.to_dict('records') if df_jobs is not None else []
        
        for j in jobs:
          source = sources[j['source']]
          is_active_or_last_job = j["status"] == "in progress" or len([jj for jj in jobs if j["source"] == jj["source"] and jj["start_on"] > j["start_on"]]) == 0
          dls = j['dls_json']
          tag_name = dls["scope"]["tags"][0] if "tags" in dls["scope"] and len(dls["scope"]["tags"]) > 0 else source["name"]
          if tag_name in tags:
            tag = tags[tag_name]
          else:
            tag = {
              "name":tag_name,
              "files":0,
              "size":0,
              "progress":0.0,
              "issues":0,
              "last_import_start":None,
              "last_import_end":None,
              "next_check":None
            }
            tags[tag_name] = tag
          if source["next_exec"] is not None and (tag["next_check"] is None or tag["next_check"] > str(source["next_exec"])):
            tag["next_check"] = str(source["next_exec"])
          
          if is_active_or_last_job and type(j["source_files"]) == list:
            tag["progress"] = (tag["progress"]*tag["files"] + j['progress']*len(j["source_files"]))/(tag["files"] + len(j["source_files"]))
            tag["files"] = tag["files"] + len(j["source_files"])
            tag["size"] =  tag["size"] + sum(j["file_sizes"])
            tag["issues"] =  tag["issues"] + len(df_issues[df_issues['job_id']==j["id"]] if df_issues is not None else [])
            
            if tag["last_import_start"] is None or tag['last_import_start'] < str(j['start_on']):
                tag["last_import_start"] = str(j["start_on"])
            if tag["last_import_end"] is None or (j["end_on"] is not None and str(j["end_on"]) > tag["last_import_end"]):
              tag['last_import_end'] = str(j['end_on'])
            if ("step" not in tag) or tag["progress"] < j["progress"]:
                tag['status'] = j['status']
                tag['step'] = j["step"]
          else:
            if tag["last_import_end"] is None or (j["end_on"] is not None and str(j["end_on"]) > tag["last_import_end"]):
              tag['last_import_end'] = str(j['end_on'])
              
        res = list(tags.values())
        res.sort(key = lambda s:s["name"]) 
        response = {'sources' : res}
        self.write(response)

class JobsBySourceHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy, pipeline_proxy):
        self.storage_proxy = storage_proxy
        self.pipeline_proxy = pipeline_proxy
    def get(self):
        """
        ---
        tags:
          - Jobs
        summary: List of jobs related to a source
        description: List of jobs for a particular source including job_id, start, end, status, step, dls file and number of issues.
        operationId: getJobs
        parameters:
          - name: source
            in: query
            description: source name
            required: false
            schema:
              type: string
        responses:
            '200':
              description: List of jobs for a particular source including job_id, start, end, status, step, dls, files, number of issues
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/JobsModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/JobsModel'
                text/plain:
                  schema:
                    type: string
        """
        source = self.get_argument('source', default = None)
        df_issues = self.storage_proxy.read_db('issue').get()
        df_jobs = self.storage_proxy.read_db('job').get()
        jobs_list = []
        for j in df_jobs.to_dict('records'):
          dls = j['dls_json']
          tag_name = dls["scope"]["tags"][0] if "tags" in dls["scope"] and len(dls["scope"]["tags"]) > 0 else j["source"]
          if source is None or source == tag_name: 
            jobs_list.append(
              {'id': j['id'],
                'source': str(j['source']),
                'start': str(j['start_on']),
                'end': str(j['end_on']),
                'status': j['status'],
                'step': j['step'],
                #'dls': j['dls_json'],
                'progress': j['progress'],
                'files': len(j['source_files']) if type(j["source_files"]) == list else None,
                'size': sum(j['file_sizes']) if type(j["file_sizes"]) == list else None,
                'issues': len(df_issues[(df_issues['source']==j['source']) & (df_issues['job_id']==j['id'])]) if df_issues is not None else 0
              } 
            )
        jobs_list.sort(key = lambda j:j['id'], reverse = True)      
        response = {'jobs' : jobs_list}
        self.write(response)

    def delete(self):
        """
        ---
        tags:
          - Jobs
        summary: Force a job to be failed and delete all its data
        description: Force a job to be failed and delete all its data
        operationId: failJobs
        parameters:
          - name: job_id
            in: query
            description: job id to delete
            required: true
            schema:
              type: int
        responses:
            '200':
              description: id of deleted job
              content:
                text/plain:
                  schema:
                    type: string
        """
        job_id = self.get_argument('job_id', default = None)
        self.pipeline_proxy.fail_job(int(job_id), delete_job = True).get()
        self.write(job_id)

class IssuesHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy):
        self.storage_proxy = storage_proxy
    def get(self):
        """
        ---
        tags:
          - issues
        summary: List of issues realted to a Job of a source
        description: List of issues produced  for a particular job in a source.
        operationId: getIssues
        parameters:
          - name: source
            in: query
            description: source name
            required: false
            schema:
              type: string
          - name: job_id
            in: query
            description: job id
            required: false
            schema:
              type: int
        responses:
            '200':
              description: List of issues found during job of sources
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/IssueModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/IssueModel'
                text/plain:
                  schema:
                    type: string
        """
        source = self.get_argument('source', default = None)
        job = self.get_argument('job_id', default = None)

        sources = list(self.storage_proxy.read_db('source').get()['name'])
        if source is not None and source not in sources:
            self.set_status(400)
            return self.write("Invalid or not found source")
        else:
            df_jobs = self.storage_proxy.read_db('job').get()
            if source is not None:
              df_jobs = df_jobs[df_jobs['source']==source]
            if job is not None:
              df_jobs = df_jobs[df_jobs['id'].astype(int)==int(job)]

            df_issues = self.storage_proxy.read_db('issue').get()
            if df_jobs is not None:
              dlss = {j['source']:j['dls_json'] for j in df_jobs.to_dict('records')}
            else :
              dlss = {}
            tags = {source:dls["scope"]["tags"][0] if "tags" in dls["scope"] and len(dls["scope"]["tags"]) > 0 else source for source, dls in dlss.items()}

            if df_issues is not None:
              df_issues = df_issues[df_issues['job_id'].isin(df_jobs['id'])]
              df_issues = df_issues.copy()
              df_issues["raised_on"] = df_issues["raised_on"].astype(str)
              df_issues["tag"] = df_issues['source'].apply(lambda s: tags[s])

              issue_list = df_issues.to_dict('records') 
            else:
              issue_list = []
        response = {'issues' : issue_list}
        self.write(response)


class SourceDetailsHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy):
        self.storage_proxy = storage_proxy
    def get(self):
        """
        ---
        tags:
          - Source Details
        summary: List of source details as per data labelling schema
        description: List of sources detauks as oer data labelling schema
        operationId: getSourceDetails
        parameters:
          - name: source
            in: query
            description: source name
            required: false
            schema:
              type: string
        responses:
            '200':
              description: List of data labelling schema for the sources
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/SourceDetailModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/SourceDetailModel'
                text/plain:
                  schema:
                    type: string
        """
        source = self.get_argument('source', default = None)
        sources_path = util.pandem_path("files", "source-definitions")
        dls_paths = self.storage_proxy.list_files(sources_path).get()
        dlss = [self.storage_proxy.read_file(f['path']).get() for f in dls_paths if f['path'].endswith(".json")]
        defs = {dls["scope"]["tags"][0]+ " - "+ dls["scope"]["source"] if "tags" in dls["scope"] and len(dls["scope"]["tags"]) > 0 else dls["scope"]["source"]:dls for dls in dlss}
        if source is not None:
          defs = {k:v for k, v in defs.items() if k == source}
        response = {'sources':list(defs.keys()), 'definitions':defs }
        self.write(response)

class VariableListHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy, variables_proxy):
        self.storage_proxy = storage_proxy
        self.variables_proxy = variables_proxy
    def get(self):
        """
        ---
        tags:
          - Variable List
        summary: List of used variables on this PANDEM-2 instance
        description: List variables published on this PANDEM-2 instace
        operationId: getVariableList
        parameters:
        responses:
            '200':
              description: List of variables and mofifiers
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/VariableListModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/VariableListModel'
                text/plain:
                  schema:
                    type: string
        """


        var_path = util.pandem_path("files", "variables")
        var_paths = self.storage_proxy.list_files(var_path, include_files = False, include_dirs = True, recursive = False).get()
        var_dic = self.variables_proxy.get_variables().get()
        
        pub_vars = {v['path'] for v in var_paths }

        sources_path = util.pandem_path("files", "source-definitions")
        dls_paths = self.storage_proxy.list_files(sources_path).get()
        dlss = [self.storage_proxy.read_file(f['path']).get() for f in dls_paths if f['path'].endswith(".json")]
        used_vars = {col["variable"] for dls in dlss for col in dls['columns'] if "variable" in col}
        found_vars = {}
        for v in var_dic:
          if v in used_vars or v in pub_vars: 
             found_vars[v] = var_dic[v].copy()
             found_vars[v].pop("aliases")
             found_vars[v]["base_variable"] = found_vars[v]["variable"] if  found_vars[v]["variable"] != v else None
             found_vars[v]["variable"] = v
        ret = list(found_vars.values())
        ret.sort(key = lambda v: v["data_family"]+"_"+v["variable"])
        response = {'variables':ret}
        self.write(response)


class TimeSerieHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy, variables_proxy):
        self.storage_proxy = storage_proxy
        self.variables_proxy = variables_proxy
    def post(self):
        """
        ---
        tags:
          - Time series
        summary: Retrieve infromation about time series avaiable in this PANDEM-2 instance
        description: Time series available in PANDEM-2
        operationId: getTimeSeries
        parameters:
        responses:
            '200':
              description: List of time series available
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/TimeSerieModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/TimeSerieModel'
                text/plain:
                  schema:
                    type: string
        """
        storage_proxy = self.storage_proxy
        variables_proxy = self.variables_proxy
        var_dic = variables_proxy.get_variables().get()
        query = tornado.escape.json_decode(self.request.body)
        if query is not None:
          ts = variables_proxy.get_timeseries().get()
          comb = [(k, v) for (k,v) in query.items() if v is not None and k != 'indicator' and k != 'source']
          comb.sort(key = lambda v: v[0])
          source = query["source"]
          indicator = query["indicator"]
          variable = var_dic[indicator]["variable"]
          datevars = [v for v, varinfo in var_dic.items() if varinfo['type']=='date' and varinfo['variable']==v]

          data = variables_proxy.lookup([variable], source = source, combinations = [tuple(comb)], filter = {d:None for d in datevars}).get()
          # making an aggregation at day level
          resp = {}
          for key, values in data.items():
            for var, tuples in values.items():
              for t in tuples:
                value = t["value"]
                for datevar, dtime in t["attrs"].items():
                  date = dtime[0:10]
                  if (date, datevar) not in resp:
                    resp[(date, datevar)] = {'date':date, 'date_var':datevar, "key":json.dumps({k:v for k,v in key})}
                    #resp[(date, datevar)].update({k:v for k,v in keys})
                  if var not in resp[(date, datevar)]:
                    resp[(date, datevar)]["indicator"] = indicator
                    resp[(date, datevar)]["value"] = value
                  else :
                    # TODO: change the aggregation function depending on the unit
                    resp[(date, datevar)]["value"] = resp[(date, datevar)]["value"] + value
                    
        response = {"timeserie":list(resp.values())}
        self.write(response)

class TimeSeriesHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy, variables_proxy):
        self.storage_proxy = storage_proxy
        self.variables_proxy = variables_proxy
        self._timeseries_hash = ''
        self._timeseries_cache = ''
    def get(self):
        """
        ---
        tags:
          - Time series
        summary: Retrieve data of a particular time serie defined by its combination filer passed as json port
        description: Get time serie data
        operationId: getTimeSerie
        parameters:
        responses:
            '200':
              description: Data of time serie
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/TimeSeriesModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/TimeSeriesModel'
                text/plain:
                  schema:
                    type: string
        """
        storage_proxy = self.storage_proxy
        variables_proxy = self.variables_proxy
        # If no changes have been performed on timeseries and we have a let's try to reuse last value
        if self._timeseries_cache != '' and self._timeseries_hash != '' and self._timeseries_hash == self.variables_proxy.timeseries_hash.get():
            self.write(self._timeseries_cache)
        else:
            # recalculating time series
            dlss = [storage_proxy.read_file(f["path"]).get() for f in storage_proxy.list_files(util.pandem_path("files", "source-definitions")).get() if f["name"].endswith(".json")]
            source_names = {dls["scope"]["source"]:dls["scope"]["tags"][0] if "tags" in dls["scope"] and len(dls["scope"]["tags"]) > 0 else dls["scope"]["name"] for dls in dlss}
            reference_users = {dls["scope"]["source"]:dls["scope"]["reference_user"] if "reference_user" in dls["scope"] else "" for dls in dlss}
            data_quality = {dls["scope"]["source"]:dls["scope"]["data_quality"] if "data_quality" in dls["scope"] else "" for dls in dlss}
            source_descriptions = {dls["scope"]["source"]:dls["scope"]["source_description"] if "source_description" in dls["scope"] else "" for dls in dlss}
            var_dic = variables_proxy.get_variables().get()
            
            # getting referential aliases
            ref_labels = {code:k for k, varinfo in var_dic.items() if varinfo["type"] == "referential_label" for code in varinfo["linked_attributes"]}
            ref_attrs = {}
            ref_link = {}
            for k, varinfo in var_dic.items(): 
              if varinfo["type"] in ["characteristic", "referential_parent" ] and varinfo['linked_attributes'] is not None: 
                for code in varinfo["linked_attributes"]:
                  if code not in ref_attrs:
                    ref_attrs[code]= []
                  ref_attrs[code].append(k)
                  ref_link[k]=code
                  
            code_labels = {}
            code_attrs = {}
            no_labels = ["indicator__description", "source__reference_user", "source__source_description"]
            ts = variables_proxy.get_timeseries().get()
            self._timeseries_hash = variables_proxy.timeseries_hash.get()
            ts_values = [{k:v for k, v in key} for key in ts.keys()]
            # Adding nice to have information on time series
            for values in ts_values:
              # Adding related attribute characteristics
              for var, value in list(values.items()):
                if var in ref_attrs:
                  # Loading referential attrs if present 
                  for attr in  ref_attrs[var]:
                    if attr not in code_attrs:
                       link = variables_proxy.get_referential(var).get()
                    if link is not None:
                      code_attrs[attr] = {t['attr'][var]:t['attrs'][attr] for t in link if 'attrs' in t and 'attr' in t and attr in t['attrs'] and var in t['attr']}
                    # Taking label from referential
                    if attr in code_attrs and value in code_attrs[attr]:
                      values[f"ref__{attr}"] = code_attrs[attr][value]

              # Adding frienly labels
              for var, value in list(values.items()):
                var = var.split("__")[-1]
                if var in ref_labels:
                  # if variable is a characteristic with a link to a referential we have to use the referential as query table
                  if var not in ref_link:
                    label_name = f"{var}_label"
                    ref_var = var 
                  else:
                    ref_var = ref_link[var]
                    label_name = f"ref__{var}_label"
                  
                  # Loading referential labels if present 
                  label = ref_labels[ref_var]
                  if ref_var not in code_labels:
                    labels = variables_proxy.get_referential(label).get()
                    if labels is not None:
                      code_labels[ref_var] = {t['attrs'][ref_var]:t['attr'][label] for t in labels if 'attrs' in t and 'attr' in t and label in t['attr'] and ref_var in t['attrs']}
                  # Taking label from referential if exists
                  if ref_var in code_labels and value in code_labels[ref_var]:
                    values[label_name] = code_labels[ref_var][value]
                  # Taking code as value if not Nont 
                  elif value is not None:
                    values[label_name] = str(value) 
                  else:
                    values[label_name] = None
                  # Making case correction when possible
                  #if values[label_name] is not None and len(values[label_name])>2: #and ref_var not in no_labels:
                  #  values[label_name] = " ".join([(word[0].upper()+word[1:].lower() if len(word)>2 else word)  for word in re.split("_| |\\-", values[label_name])])

              # Adding indicator associated values
              if "indicator" in values:
                values["indicator__family"] = var_dic[values["indicator"]]["data_family"]
                values["indicator__description"] = var_dic[values["indicator"]]["description"]
                values["indicator__unit"] = var_dic[values["indicator"]]["unit"]
              # Adding source (DLS) associated values
              if "source" in values:
                values["source__table"] = values["source"]
                values["source__source_name"] = source_names[values["source"]]
                values["source__reference_user"] = reference_users[values["source"]]
                values["source__source_description"] = source_descriptions[values["source"]]
                values["source__data_quality"] = data_quality[values["source"]]


            response = {"timeseries":ts_values}
            self._timeseries_cache = response
            self.write(response)

class DatasetHandler(tornado.web.RequestHandler):
    def initialize(self, storage_proxy, variables_proxy):
        self.storage_proxy = storage_proxy
        self.variables_proxy = variables_proxy

    def post(self):
        """
        ---
        tags:
          - Get Data Set
        summary: Retrieve infromation about time series avaiable in this PANDEM-2 instance
        description: specific dataset if available in PANDEM-2
        operationId: getDataSet
        parameters:
        responses:
            '200':
              description: Returns a specific dataset if available
              content:
                application/json:
                  schema:
                    $ref: '#/components/schemas/DatasetModel'
                application/xml:
                  schema:
                    $ref: '#/components/schemas/DatasetModel'
                text/plain:
                  schema:
                    type: string
        """
        storage_proxy = self.storage_proxy
        variables_proxy = self.variables_proxy
        var_dic = variables_proxy.get_variables().get()
        
        query = tornado.escape.json_decode(self.request.body)
        if query is not None:
            ts = variables_proxy.get_timeseries().get()
            needed_variables, query = self.__build_needed_variables(query, var_dic)
            filtered_ts = self.__filter_ts(query, needed_variables, ts)

            # Getting columns of the dataframe
            data = {}
            columns = {'source'}
            for ((source, indicator), comb) in filtered_ts.items():
                d = variables_proxy.lookup([var_dic[indicator]['variable']], source=source,
                                          combinations=comb, filter={'reporting_period': None}).get()
                data[(source, indicator)] = d
                columns.add(indicator)

                # Identifying columns from data keys
                for ts_key in d.keys():
                    for k, v in ts_key:
                        columns.add(k)
                # Retrieving columns from nested attrs
                for ts_dict in d.values():
                    for ts_values in ts_dict.values():
                        if len(ts_values) > 0 and 'attrs' in ts_values[0]:
                            columns.update(ts_values[0]['attrs'].keys())

            # Filling the dataframe with values
            rows = {}
            for ((source, indicator), v) in data.items():
                for ts_key, ts_dict in v.items():
                    for ts_values in ts_dict.values():
                        for ts_value in ts_values:
                            attrs_date_key = list(ts_value['attrs'].keys())[0]
                            if var_dic[attrs_date_key]['type'] == 'date':
                                date_element = (
                                    attrs_date_key, ts_value['attrs'][attrs_date_key])
                                row_key = list(ts_key)
                                row_key.append(date_element)
                                row_key = tuple(row_key)
                                if row_key not in rows:
                                    rows[row_key] = self.__init_row(
                                        ts_key, columns, date_element, source)
                            rows[row_key] = self.__update_indicator(
                                ts_value, rows, row_key, date_element, indicator)

            df = pd.DataFrame.from_dict(rows, orient='index', dtype=None)
            df = df.replace({np.nan: None})
            self.write({"dataset": df.to_dict('records')})


    def __build_needed_variables(self, query, var_dic):
        """Build a list of needed_variables and adds required filters"""
        needed_variables = []
        for el in query['select']:
            if var_dic[el]['type'] not in ['observation', 'indicator', 'resource', 'date']:
                needed_variables.append(var_dic[el]['variable'])
            for modifier in var_dic[el]['modifiers']:
                query['filter'][modifier['variable']] = modifier['value']

        needed_variables.extend(query['filter'].keys())
        return list(set(needed_variables)), query
    
    def __filter_ts(self, query, needed_variables, ts):
        """Keep the timeseries which have both needed_variables and proper filters"""
        filtered_ts = {}

        for k, v in ts.items():
            is_in_filter, is_in_needed = True, True
            for nv in needed_variables:
                if nv not in list(map(lambda v: v[0], k)):
                    is_in_needed = False
                    break
            if is_in_needed:
                for k2, v2 in query['filter'].items():
                    if k2 not in list(map(lambda x: x[0], k)):
                        is_in_filter = False
                        break
                    if v2 not in list(map(lambda x: x[1], k)):
                        is_in_filter = False
                        break
            if is_in_filter and is_in_needed:
                comb = [(i, j) for (i, j) in k if j is not None and i !=
                        'indicator' and i != 'source']
                comb.sort(key=lambda v: v[0])

                source = [(i, j)
                          for (i, j) in k if j is not None and i == 'source'][0][1]
                indicator = [(i, j)
                            for (i, j) in k if j is not None and i == 'indicator'][0][1]
                if (source, indicator) not in filtered_ts:
                    filtered_ts[(source, indicator)] = set()
                filtered_ts[(source, indicator)].add(tuple(comb))
        return filtered_ts
    
    def __init_row(self, ts_key, columns, date_element, source):
        """Initialize dictionary's columns and add value if not indicator"""
        row = {}
        for col in columns:
            tuples_keys = list(map(lambda x: x[0], ts_key))
            tuples_values = list(map(lambda x: x[1], ts_key))
            if col in tuples_keys:
                row[col] = tuples_values[tuples_keys.index(col)]
            else:
                row[col] = None
        row[date_element[0]] = date_element[1]
        row['source'] = source
        return row
    
    def __update_indicator(self, ts_value, rows, row_key, date_element, indicator):
        """Updates a dictionary with all indicators values"""
        if ts_value['attrs']:
            for i, j in ts_value['attrs'].items():
                if i == date_element[0]:
                    rows[row_key][indicator] = ts_value['value']
                    return rows[row_key]


@components.schemas.register
class SourcesModel(object):
    """
    ---
    type: object
    description: Sources model representation
    properties:
        sources:
            type: array
    """

@components.schemas.register
class JobsModel(object):
    """
    ---
    type: object
    description: Sources model representation
    properties:
        Jobs:
            type: array
    """

@components.schemas.register
class IssueModel(object):
    """
    ---
    type: object
    description: Issue model representation
    properties:
        issues:
            type: array
    """

@components.schemas.register
class SourceDetailModel(object):
    """
    ---
    type: object
    description: Source detail model representation
    properties:
        sources:
            type: array
        definitions:
            type: dict
    """

@components.schemas.register
class VariableListModel(object):
    """
    ---
    type: object
    description: Variable List model representation
    properties:
        variables:
            type: array
    """

@components.schemas.register
class TimeSeriesModel(object):
    """
    ---
    type: array
    description: List of variables characterizing all time series
    properties:
        timeseries:
            type: array
    """

@components.schemas.register
class DatasetModel(object):
    """
    ---
    type: array
    description: Dataset characterizing a time serie
    properties:
        dataset:
            type: array
    """


class Application(tornado.web.Application):

    def __init__(self, storage_proxy, variables_proxy, pipeline_proxy):
        settings = {"debug": False}
        self._routes = [
          tornado.web.url(r"/jobs", JobsBySourceHandler, {'storage_proxy': storage_proxy, 'pipeline_proxy':pipeline_proxy}),
          tornado.web.url(r"/sources", SourcesHandler, {'storage_proxy': storage_proxy}),
          tornado.web.url(r"/issues", IssuesHandler, {'storage_proxy': storage_proxy}),
          tornado.web.url(r"/source_details", SourceDetailsHandler, {'storage_proxy': storage_proxy}),
          tornado.web.url(r"/variable_list", VariableListHandler, {'storage_proxy': storage_proxy, 'variables_proxy':variables_proxy}),
          tornado.web.url(r"/timeseries", TimeSeriesHandler, {'storage_proxy': storage_proxy, 'variables_proxy':variables_proxy}),
          tornado.web.url(r"/timeserie", TimeSerieHandler, {'storage_proxy': storage_proxy, 'variables_proxy':variables_proxy}),
          tornado.web.url(r"/dataset", DatasetHandler, {'storage_proxy': storage_proxy, 'variables_proxy':variables_proxy})
        ]
        setup_swagger(
            self._routes,
            swagger_url="/",
            description="",
            api_version="1.0.0",
            title="Pandem source API"
        )
        super(Application, self).__init__(self._routes, **settings)
