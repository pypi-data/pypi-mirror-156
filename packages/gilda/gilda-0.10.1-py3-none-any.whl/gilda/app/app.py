from textwrap import dedent

from flask import Flask, Response, abort, jsonify, render_template, request
from flask_bootstrap import Bootstrap
from flask_restx import Api, Resource, fields
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, \
    SelectMultipleField
from wtforms.validators import DataRequired

from gilda.api import *
from gilda import __version__ as version
from gilda.resources import popular_organisms, organism_labels

app = Flask(__name__)
app.config['RESTX_MASK_SWAGGER'] = False
app.config['WTF_CSRF_ENABLED'] = False
app.config['SWAGGER_UI_DOC_EXPANSION'] = 'list'
Bootstrap(app)


class GroundForm(FlaskForm):
    text = StringField(
        'Text',
        validators=[DataRequired()],
        description=dedent("""\
            Input the entity text (e.g., <code>k-ras</code>) to ground."""
            #Click <a type="button" href="#" data-toggle="modal" data-target="#text-modal">
            #here <i class="far fa-question-circle">
            #</i></a> for more information
        ),
    )
    context = TextAreaField(
        'Context (optional)',
        description=dedent("""\
            Optionally provide additional text context to help disambiguation. Click
            <a type="button" href="#" data-toggle="modal" data-target="#context-modal">
            here <i class="far fa-question-circle">
            </i></a> for more details.
        """)
    )
    organisms = SelectMultipleField(
        'Species priority (optional)',
        choices=[(org, organism_labels[org]) for org in popular_organisms],
        id='organism-select',
        description=dedent("""\
            Optionally select one or more taxonomy
            species IDs to define a species priority list.  Click
            <a type="button" href="#" data-toggle="modal" data-target="#species-modal">
            here <i class="far fa-question-circle">
            </i></a> for more details.
        """),
    )
    submit = SubmitField('Submit')

    def get_matches(self):
        return ground(self.text.data, context=self.context.data,
                      organisms=self.organisms.data)


@app.route('/', methods=['GET', 'POST'])
def home():
    text = request.args.get('text')
    if text is not None:
        context = request.args.get('context')
        organisms = request.args.getlist('organisms')
        matches = ground(text, context=context, organisms=organisms)
        return render_template('matches.html', matches=matches, version=version,
                               text=text, context=context)

    form = GroundForm()
    if form.validate_on_submit():
        matches = form.get_matches()
        return render_template('matches.html', matches=matches, version=version,
                               text=form.text.data, context=form.context.data)
    return render_template('home.html', form=form, version=version)


# NOTE: the Flask REST-X API has to be declared here, below the home endpoint
# otherwise it reserves the / base path.

api = Api(app,
          title="Gilda",
          description="A service for grounding entity strings",
          version=version,
          license="Code available under the BSD 2-Clause License",
          contact="INDRA labs",
          contact_email="indra.sysbio@gmail.com",
          contact_url="https://indralab.github.io",
          doc='/apidocs',
          )

base_ns = api.namespace('Gilda API', 'Gilda API', path='/')

grounding_input_model = api.model(
    "GroundingInput",
    {'text': fields.String(example='EGF-receptor',
                           required=True,
                           description='The entity string to be grounded.'),
     'context': fields.String(example='The EGFR-receptor binds EGF.',
                              required=False,
                              description='Surrounding text as context to aid'
                                          ' disambiguation when applicable.'),
     'organisms': fields.List(fields.String, example=['9606'],
                              description='An optional list of taxonomy '
                                          'species IDs defining a priority list'
                                          ' in case an entity string can be '
                                          'resolved to multiple'
                                          'species-specific genes/proteins.',
                              required=False)}
)

term_model = api.model(
    "Term",
    {'norm_text' : fields.String(
        description='The normalized text corresponding to the text entry, '
                    'used for lookups.',
        example='egf receptor'),
     'text' : fields.String(
         description='The text entry that was matches.',
         example='EGF receptor'
     ),
     'db' : fields.String(
         description='The database / namespace corresponding to the '
                     'grounded term.',
         example='HGNC'
     ),
     'id': fields.String(
         description='The identifier of the grounded term within the '
                     'database / namespace.',
         example='3236'
     ),
     'entry_name': fields.String(
         description='The standardized name corresponding to the grounded '
                     'term.',
         example='EGFR'
     ),
     'status': fields.String(
         description='The relationship of the text entry to the grounded '
                     'term, e.g., synonym.',
         example='curated'
     ),
     'source': fields.String(
         description='The source from which the term was obtained.',
         example='famplex'
     ),
     'organism': fields.String(
         description='If the term is a gene/protein, this field provides '
                     'the taxonomy identifier of the species to which '
                     'it belongs.',
         example='9606'
     ),
     'source_db': fields.String(
         description='In some cases the term\'s db/id was mapped from another '
                     'db/id pair given in the original source. If this is the '
                     'case, this field provides the original source db.'),
     'source_id': fields.String(
         description='In some cases the term\'s db/id was mapped from another '
                     'db/id pair given in the original source. If this is the '
                     'case, this field provides the original source ID.')
    }
)

scored_match_model = api.model(
    "ScoredMatch",
    {'term': fields.Nested(term_model,
                           description='The term that was matched'),
     'url': fields.String(
         description='Identifiers.org URL for the matched term.',
         example='https://identifiers.org/hgnc:3236'
     ),
     'score': fields.Float(
         description='The score assigned to the matched term.',
         example=0.9845
     ),
     'match': fields.Nested(api.model('Match', {}),
         description='Additional metadata about the nature of the match.'
     ),
     'subsumed_terms': fields.List(fields.Nested(term_model),
         description='In some cases multiple terms with the same db/id '
                     'matched the input string, potentially with different '
                     'scores, and only the first one is exposed in the '
                     'scored match\'s term attribute (see above). This field '
                     'provides additional terms with the same db/id that '
                     'matched the input for additional traceability.')
     }
)


get_names_input_model = api.model(
    "GetNamesInput",
    {'db': fields.String(
        description="Capitalized name of the database for the grounding, "
                    "e.g. HGNC.",
        required=True,
        example='HGNC'),
     'id': fields.String(
         description="Identifier within the given database",
         required=True,
         example='3236'
     ),
     'status': fields.String(
         description="If provided, only entity texts of the given status are "
                     "returned (e.g., curated, name, synonym, former_name).",
         required=False,
         enum=['curated', 'name', 'synonym', 'former_name'],
         example='synonym'
     ),
     'source': fields.String(
         description="If provided, only entity texts collected from the given "
                     "source are returned.This is useful if terms grounded to "
                     "IDs in a given database are collected from multiple "
                     "different sources.",
         required=False,
         example='uniprot'
     )
    }
)

names_model = fields.List(
        fields.String,
        example=['EGF receptor', 'EGFR', 'ERBB1', 'Proto-oncogene c-ErbB-1'])

models_model = fields.List(
    fields.String,
    example=['A4', 'ABC1', 'p180'])


@base_ns.route('/ground', methods=['POST'])
class Ground(Resource):
    # NOTE: formally this response should be a list
    @base_ns.response(200, "Grounding results", [scored_match_model])
    @base_ns.expect(grounding_input_model)
    def post(self):
        """Return a list of scored grounding matches for a given entity text.

        The returned value is a list with each entry being a scored match.
        Each scored match contains a term which was matched, and each term
        contains a db and id constituting a grounding. An empty list
        return value means that no grounding matches were found for the input.
        """
        if request.json is None:
            abort(Response('Missing application/json header.', 415))
        # Get input parameters
        text = request.json.get('text')
        context = request.json.get('context')
        organisms = request.json.get('organisms')
        scored_matches = ground(text, context=context, organisms=organisms)
        res = [sm.to_json() for sm in scored_matches]
        return jsonify(res)


@base_ns.route('/names', methods=['POST'])
@base_ns.route('/get_names', methods=['POST'])
class GetNames(Resource):
    @base_ns.response(200, "Get names result", names_model)
    @base_ns.expect(get_names_input_model)
    def post(self):
        """Return all known entity texts for a grounding.

        This endpoint can be used as a reverse lookup to find out what entity
        texts (names, synonyms, etc.) are known for a given grounded entity.
        """
        if request.json is None:
            abort(Response('Missing application/json header.', 415))
        # Get input parameters
        kwargs = {key: request.json.get(key) for key in {'db', 'id', 'status',
                                                         'source'}}
        names = get_names(**kwargs)
        return jsonify(names)


@base_ns.route('/models', methods=['GET', 'POST'])
class GetModels(Resource):
    @base_ns.response(200, "Get models result", models_model)
    def post(selt):
        """Return a list of texts with Gilda disambiguation models.

        Gilda makes available more than one thousand disambiguation models
        between synonyms shared by multiple genes. This endpoint returns
        the list of entity texts for which such a model is available.
        """
        return jsonify(get_models())

    def get(self):
        """Return a list of texts with Gilda disambiguation models.

        Gilda makes available more than one thousand disambiguation models
        between synonyms shared by multiple genes. This endpoint returns
        the list of entity texts for which such a model is available.
        """
        return jsonify(get_models())
