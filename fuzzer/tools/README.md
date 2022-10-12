# generating data files

```
$ cd cur_dir
$ export export __GEN_SPEC=1
$ import_apis.py --glspec ../../scripts/webgl_fuzz/webgl1_spec.json  --output spec_v1.pickle --json v1.json
$ python import_apis.py --glspec ../../scripts/webgl_fuzz/webgl2_spec.json  --output spec_v2.pickle --json v2.json
$ cp spec_v1.pickle ../program/api_spec
$ cp spec_v2.pickle ../program/api_spec
$ cp v1.json ../test_runner/v1.json
$ cp v2.json ../test_runner/v2.json

unset __GEN_SPEC
```


# generating api dependencies

The static analyzer in `phasar/build_Release/unittests/PhasarLLVM/DataFlowSolver/IfdsIde/Problems/glanalysis/glanalysis_unittest`.
The results are stored in `tools/glanalyzer/webgl-specs/v{1, 2}.json.res.json`

To generate the dep result: 

``` sh
./import_api_dep.py --dep_res ~/data/llvm-experiment/phasar/tools/glanalyzer/webgl-specs/v1.json.res.json
mv apidep.pickle apidep_v1.pickle
./import_api_dep.py --dep_res ~/data/llvm-experiment/phasar/tools/glanalyzer/webgl-specs/v2.json.res.json
mv apidep.pickle apidep_v2.pickle
```
