# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------
import importlib

import qiime2.plugin
from q2_types.per_sample_sequences import (
    SequencesWithQuality, PairedEndSequencesWithQuality)
from q2_types.sample_data import SampleData
from q2_types.feature_data import FeatureData, Sequence
from q2_types.feature_table import FeatureTable, Frequency

import q2_dada2
from q2_dada2 import DADA2Stats, DADA2StatsFormat, DADA2StatsDirFmt

_CHIM_OPT = {'pooled', 'consensus', 'none'}

plugin = qiime2.plugin.Plugin(
    name='dada2',
    version=q2_dada2.__version__,
    website='http://benjjneb.github.io/dada2/',
    package='q2_dada2',
    description=('This QIIME 2 plugin wraps DADA2 and supports '
                 'sequence quality control for single-end and paired-end '
                 'reads using the DADA2 R library.'),
    short_description='Plugin for sequence quality control with DADA2.',
    citations=qiime2.plugin.Citations.load('citations.bib', package='q2_dada2')
)


plugin.methods.register_function(
    function=q2_dada2.denoise_single,
    inputs={'demultiplexed_seqs': SampleData[SequencesWithQuality |
                                             PairedEndSequencesWithQuality]},
    parameters={'trunc_len': qiime2.plugin.Int,
                'trim_left': qiime2.plugin.Int,
                'max_ee': qiime2.plugin.Float,
                'trunc_q': qiime2.plugin.Int,
                'chimera_method': qiime2.plugin.Str %
                qiime2.plugin.Choices(_CHIM_OPT),
                'min_fold_parent_over_abundance': qiime2.plugin.Float,
                'n_threads': qiime2.plugin.Int,
                'n_reads_learn': qiime2.plugin.Int,
                'hashed_feature_ids': qiime2.plugin.Bool},
    outputs=[('table', FeatureTable[Frequency]),
             ('representative_sequences', FeatureData[Sequence]),
             ('denoising_stats', SampleData[DADA2Stats])],
    input_descriptions={
        'demultiplexed_seqs': ('The single-end demultiplexed sequences to be '
                               'denoised.')
    },
    parameter_descriptions={
        'trunc_len': ('Position at which sequences should be truncated due to '
                      'decrease in quality. This truncates the 3\' end of the '
                      'of the input sequences, which will be the bases that '
                      'were sequenced in the last cycles. Reads that are '
                      'shorter than this value will be discarded. If 0 is '
                      'provided, no truncation or length filtering will be '
                      'performed'),
        'trim_left': ('Position at which sequences should be trimmed due to '
                      'low quality. This trims the 5\' end of the '
                      'of the input sequences, which will be the bases that '
                      'were sequenced in the first cycles.'),
        'max_ee': ('Reads with number of expected errors higher than this '
                   'value will be discarded.'),
        'trunc_q': ('Reads are truncated at the first instance of a quality '
                    'score less than or equal to this value. If the resulting '
                    'read is then shorter than `trunc_len`, it is discarded.'),
        'chimera_method': ('The method used to remove chimeras. '
                           '"none": No chimera removal is performed. '
                           '"pooled": All reads are pooled prior to chimera '
                           'detection. "consensus": Chimeras are detected in '
                           'samples individually, and sequences found '
                           'chimeric in a sufficient fraction of samples are '
                           'removed.'),
        'min_fold_parent_over_abundance': (
            'The minimum abundance of potential parents of a sequence being '
            'tested as chimeric, expressed as a fold-change versus the '
            'abundance of the sequence being tested. Values should be greater '
            'than or equal to 1 (i.e. parents should be more abundant than '
            'the sequence being tested). This parameter has no effect if '
            'chimera_method is "none".'),
        'n_threads': ('The number of threads to use for multithreaded '
                      'processing. If 0 is provided, all available cores will '
                      'be used.'),
        'n_reads_learn': ('The number of reads to use when training the '
                          'error model. Smaller numbers will result in a '
                          'shorter run time but a less reliable error '
                          'model.'),
        'hashed_feature_ids': ('If true, the feature ids in the resulting '
                               'table will be presented as hashes of the '
                               'sequences defining each feature. The hash '
                               'will always be the same for the same sequence '
                               'so this allows feature tables to be merged '
                               'across runs of this method. You should only '
                               'merge tables if the exact same parameters are '
                               'used for each run.')
    },
    output_descriptions={
        'table': 'The resulting feature table.',
        'representative_sequences': ('The resulting feature sequences. Each '
                                     'feature in the feature table will be '
                                     'represented by exactly one sequence.')
    },
    name='Denoise and dereplicate single-end sequences',
    description=('This method denoises single-end sequences, dereplicates '
                 'them, and filters chimeras.')
)


plugin.methods.register_function(
    function=q2_dada2.denoise_paired,
    inputs={'demultiplexed_seqs': SampleData[PairedEndSequencesWithQuality]},
    parameters={'trunc_len_f': qiime2.plugin.Int,
                'trunc_len_r': qiime2.plugin.Int,
                'trim_left_f': qiime2.plugin.Int,
                'trim_left_r': qiime2.plugin.Int,
                'max_ee_f': qiime2.plugin.Float,
                'max_ee_r': qiime2.plugin.Float,
                'trunc_q': qiime2.plugin.Int,
                'chimera_method': qiime2.plugin.Str %
                qiime2.plugin.Choices(_CHIM_OPT),
                'min_fold_parent_over_abundance': qiime2.plugin.Float,
                'n_threads': qiime2.plugin.Int,
                'n_reads_learn': qiime2.plugin.Int,
                'hashed_feature_ids': qiime2.plugin.Bool},
    outputs=[('table', FeatureTable[Frequency]),
             ('representative_sequences', FeatureData[Sequence]),
             ('denoising_stats', SampleData[DADA2Stats])],
    input_descriptions={
        'demultiplexed_seqs': ('The paired-end demultiplexed sequences to be '
                               'denoised.')
    },
    parameter_descriptions={
        'trunc_len_f': ('Position at which forward read sequences should be '
                        'truncated due to decrease in quality. This truncates '
                        'the 3\' end of the of the input sequences, which '
                        'will be the bases that were sequenced in the last '
                        'cycles. Reads that are shorter than this value '
                        'will be discarded. After this parameter is applied '
                        'there must still be at least a 20 nucleotide overlap '
                        'between the forward and reverse reads. If 0 is '
                        'provided, no truncation or length filtering will be '
                        'performed'),
        'trim_left_f': ('Position at which forward read sequences should be '
                        'trimmed due to low quality. This trims the 5\' end '
                        'of the input sequences, which will be the bases that '
                        'were sequenced in the first cycles.'),
        'trunc_len_r': ('Position at which reverse read sequences should be '
                        'truncated due to decrease in quality. This truncates '
                        'the 3\' end of the of the input sequences, which '
                        'will be the bases that were sequenced in the last '
                        'cycles. Reads that are shorter than this value '
                        'will be discarded. After this parameter is applied '
                        'there must still be at least a 20 nucleotide overlap '
                        'between the forward and reverse reads. If 0 is '
                        'provided, no truncation or length filtering will be '
                        'performed'),
        'trim_left_r': ('Position at which reverse read sequences should be '
                        'trimmed due to low quality. This trims the 5\' end '
                        'of the input sequences, which will be the bases that '
                        'were sequenced in the first cycles.'),
        'max_ee_f': ('Forward reads with number of expected errors higher '
                     'than this value will be discarded.'),
        'max_ee_r': ('Reverse reads with number of expected errors higher '
                     'than this value will be discarded.'),
        'trunc_q': ('Reads are truncated at the first instance of a quality '
                    'score less than or equal to this value. If the resulting '
                    'read is then shorter than `trunc_len_f` or `trunc_len_r` '
                    '(depending on the direction of the read) it is '
                    'discarded.'),
        'chimera_method': ('The method used to remove chimeras. '
                           '"none": No chimera removal is performed. '
                           '"pooled": All reads are pooled prior to chimera '
                           'detection. "consensus": Chimeras are detected in '
                           'samples individually, and sequences found '
                           'chimeric in a sufficient fraction of samples are '
                           'removed.'),
        'min_fold_parent_over_abundance': (
            'The minimum abundance of potential parents of a sequence being '
            'tested as chimeric, expressed as a fold-change versus the '
            'abundance of the sequence being tested. Values should be greater '
            'than or equal to 1 (i.e. parents should be more abundant than '
            'the sequence being tested). This parameter has no effect if '
            'chimera_method is "none".'),
        'n_threads': ('The number of threads to use for multithreaded '
                      'processing. If 0 is provided, all available cores will '
                      'be used.'),
        'n_reads_learn': ('The number of reads to use when training the '
                          'error model. Smaller numbers will result in a '
                          'shorter run time but a less reliable error '
                          'model.'),
        'hashed_feature_ids': ('If true, the feature ids in the resulting '
                               'table will be presented as hashes of the '
                               'sequences defining each feature. The hash '
                               'will always be the same for the same sequence '
                               'so this allows feature tables to be merged '
                               'across runs of this method. You should only '
                               'merge tables if the exact same parameters are '
                               'used for each run.')
    },
    output_descriptions={
        'table': 'The resulting feature table.',
        'representative_sequences': ('The resulting feature sequences. Each '
                                     'feature in the feature table will be '
                                     'represented by exactly one sequence, '
                                     'and these sequences will be the joined '
                                     'paired-end sequences.')
    },
    name='Denoise and dereplicate paired-end sequences',
    description=('This method denoises paired-end sequences, dereplicates '
                 'them, and filters chimeras.')
)


plugin.methods.register_function(
    function=q2_dada2.denoise_pyro,
    inputs={'demultiplexed_seqs': SampleData[SequencesWithQuality]},
    parameters={'trunc_len': qiime2.plugin.Int,
                'trim_left': qiime2.plugin.Int,
                'max_ee': qiime2.plugin.Float,
                'trunc_q': qiime2.plugin.Int,
                'max_len': qiime2.plugin.Int,
                'chimera_method': qiime2.plugin.Str %
                qiime2.plugin.Choices(_CHIM_OPT),
                'min_fold_parent_over_abundance': qiime2.plugin.Float,
                'n_threads': qiime2.plugin.Int,
                'n_reads_learn': qiime2.plugin.Int,
                'hashed_feature_ids': qiime2.plugin.Bool},
    outputs=[('table', FeatureTable[Frequency]),
             ('representative_sequences', FeatureData[Sequence]),
             ('denoising_stats', SampleData[DADA2Stats])],
    input_descriptions={
        'demultiplexed_seqs': 'The single-end demultiplexed pyrosequencing '
                              'sequences (e.g. 454, IonTorrent) to be '
                              'denoised.'
    },
    parameter_descriptions={
        'trunc_len': 'Position at which sequences should be truncated due to '
                     'decrease in quality. This truncates the 3\' end of the '
                     'of the input sequences, which will be the bases that '
                     'were sequenced in the last cycles. Reads that are '
                     'shorter than this value will be discarded. If 0 is '
                     'provided, no truncation or length filtering will be '
                     'performed',
        'trim_left': 'Position at which sequences should be trimmed due to '
                     'low quality. This trims the 5\' end of the '
                     'of the input sequences, which will be the bases that '
                     'were sequenced in the first cycles.',
        'max_ee': 'Reads with number of expected errors higher than this '
                  'value will be discarded.',
        'trunc_q': 'Reads are truncated at the first instance of a quality '
                   'score less than or equal to this value. If the resulting '
                   'read is then shorter than `trunc_len`, it is discarded.',
        'max_len': 'Remove reads prior to trimming or truncation which are '
                   'longer than this value. If 0 is provided no reads will '
                   'be removed based on length.',
        'chimera_method': 'The method used to remove chimeras. '
                          '"none": No chimera removal is performed. '
                          '"pooled": All reads are pooled prior to chimera '
                          'detection. "consensus": Chimeras are detected in '
                          'samples individually, and sequences found '
                          'chimeric in a sufficient fraction of samples are '
                          'removed.',
        'min_fold_parent_over_abundance':
            'The minimum abundance of potential parents of a sequence being '
            'tested as chimeric, expressed as a fold-change versus the '
            'abundance of the sequence being tested. Values should be greater '
            'than or equal to 1 (i.e. parents should be more abundant than '
            'the sequence being tested). This parameter has no effect if '
            'chimera_method is "none".',
        'n_threads': 'The number of threads to use for multithreaded '
                     'processing. If 0 is provided, all available cores will '
                     'be used.',
        'n_reads_learn': 'The number of reads to use when training the '
                         'error model. Smaller numbers will result in a '
                         'shorter run time but a less reliable error '
                         'model.',
        'hashed_feature_ids': 'If true, the feature ids in the resulting '
                              'table will be presented as hashes of the '
                              'sequences defining each feature. The hash '
                              'will always be the same for the same sequence '
                              'so this allows feature tables to be merged '
                              'across runs of this method. You should only '
                              'merge tables if the exact same parameters are '
                              'used for each run.'
    },
    output_descriptions={
        'table': 'The resulting feature table.',
        'representative_sequences': 'The resulting feature sequences. Each '
                                    'feature in the feature table will be '
                                    'represented by exactly one sequence.'
    },
    name='Denoise and dereplicate single-end pyrosequences',
    description='This method denoises single-end pyrosequencing sequences, '
                'dereplicates them, and filters chimeras.'
)


plugin.register_formats(DADA2StatsFormat, DADA2StatsDirFmt)
plugin.register_semantic_types(DADA2Stats)
plugin.register_semantic_type_to_format(
    SampleData[DADA2Stats], DADA2StatsDirFmt)
importlib.import_module('q2_dada2._transformer')
