var specs= [];

// $.getJSON("./v1.json", function(data) {
//     specs[1] = data;
// });

// $.getJSON("./v2.json", function(data) {
//     specs[2] = data;
// });


function load_specs() {
    $.ajax({
	url:"./v1.json",
	type:"get",
	dataType:'JSON',
	async: false,
    }).done(function(data) {
	specs[1] = data;
    });
    $.ajax({
	url:"./v2.json",
	type:"get",
	dataType:'JSON',
	async: false,
    }).done(function(data) {
	specs[2] = data;
    });
}

function assert(condition, message) {
    if (!condition) {
        throw message || "Assertion failed";
    }
}

var cvs_id = "__cvs_test_id";
var cvs = null;
var offcvs_id = "__offcvs_test_id";
// var offcvs = null;
var webgl_ctx = null;


function create_canvas(options) {
    cvs = document.createElement("canvas");
    cvs.width = options.width;
    cvs.height = options.height;
    cvs.id = cvs_id;

    // this is a canvas object shown on the DOM tree
    document.body.appendChild(cvs);
    return cvs;
}

function delete_canvas() {
    // var cvs = document.getElementById(cvs_id);

    if (cvs == null) {
        cvs = document.getElementById(cvs_id);
    }

    if (cvs != null)
        document.body.removeChild(cvs);
}


function create_offscreen_canvas(options) {
    cvs = new OffscreenCanvas(options.width, options.height);
    cvs.id = offcvs_id;
    // <canvas id="one"></canvas>
    // <canvas id="two"></canvas>

    // var one = document.getElementById("one").getContext("bitmaprenderer");
    // var two = document.getElementById("two").getContext("bitmaprenderer");


    // var offscreen = new OffscreenCanvas(256, 256);
    // var gl = offscreen.getContext('webgl');

    // ... some drawing for the first canvas using the gl context ...

    // Commit rendering to the first canvas
    // var bitmapOne = offscreen.transferToImageBitmap();
    // one.transferFromImageBitmap(bitmapOne);

    // document.body.appendChild(canvas);

    return cvs;
}

/*
function delete_offscreen_canvas() {
    var offscreen_cvs = document.getElementById(offcvs_id);

    if (offscreen_cvs != null)
        document.body.removeChild(offscreen_cvs);
}
*/

var offscreen_test = false;

function prepare_context(gl_version, canvas_width, canvas_heigth) {
    // we can assume that cur_test != null
    var options = {width:canvas_width, height:canvas_heigth};

    if (!offscreen_test)
        create_canvas(options);
    else
        create_offscreen_canvas(options);

    if (cvs == null) {
        return null;
    }

    // which ctx to create
    if (gl_version == 1) {
        webgl_ctx = cvs.getContext("webgl");
    } else {
        webgl_ctx = cvs.getContext("webgl2");
    }

    return webgl_ctx;
}


async function load_image(elem) {
	// elem.src = "images/tiny.png";

	var promise = new Promise(resolve =>  {

        elem.addEventListener("load", (e) => {
            console.log("load event received!!!");
            resolve(e);
        });

        elem.src = "images/tiny.png";

    });

    console.log("Before await");
    var res = await promise;
    console.log("After await");

	return res;
}

function handle_htmlelement_type(arg_spec, value, exec_ctx) {
    if (typeof value == "number") {
        // it is an reference
        return exec_ctx[arg_spec.arg_type][value];
    } else {
        // we should create a new object
        var tag_map = {"HTMLImageElement":"img", "HTMLVideoElement":"video", "HTMLCanvasElement":"canvas"};
        var e = null;
	if (arg_spec.arg_type == "HTMLImageElement") {
	    e = document.getElementById("img_id");
	    // e.width = 150;
	    // e.height = 200;
	} else if (arg_spec.arg_type == "HTMLVideoElement") {
	    e =  document.getElementById("video_id");
	} else {
	    e = document.createElement(tag_map[arg_spec.arg_type]);
	}

	/*         var loaded = false;

		   var promise = new Promise(function(resolve, reject) {
		   e.addEventListener("load", function(e) {
                   resolve(e);
		   });
		   }); */

        // here we have a bug, the image may be still not loaded,
        // when the api is executed.
        // if (arg_spec.arg_type == "HTMLImageElement") {
        //     // e.src = "images/tiny.png";
		// 	// var res = load_image(e);
		// 	// console.log(res);
		// 	e = document.getElementById("img_id");
        // }

	// var res = load_image
	/*
        promise.then(function(value) {
            loaded = true;
            console.log("loaded!!!!!!!!!!!!");
        });

        while (!loaded) {
            ;
        } */

        if (arg_spec.arg_type != "HTMLImageElement" && arg_spec.arg_type != "HTMLVideoElement") {
            document.body.appendChild(e);
        }
        // exec_ctx[arg_spec.arg_type]
        if (!(arg_spec.arg_type in exec_ctx)) {
            exec_ctx[arg_spec.arg_type] = [];
        }


        exec_ctx[arg_spec.arg_type].push(e);


        if (arg_spec.arg_type != "HTMLImageElement" && arg_spec.arg_type != "HTMLVideoElement") {
            exec_ctx.elements.push(e);
        }

        return e;
    }
}

function handle_offscreencanvas_type(arg_spec, value, exec_ctx) {
    if (typeof value == "number") {
        return exec_ctx[arg_spec.arg_type][value];
    }

    var cvs = new OffscreenCanvas(200, 200);

    if (!(arg_spec.arg_type in exec_ctx)) {
        exec_ctx[arg_spec.arg_type] = [];
    }
    exec_ctx[arg_spec.arg_type].push(cvs);

    return cvs;
}

function handle_imagedata_type(arg_spec, value, exec_ctx) {
    if (typeof value == "number") {
        return exec_ctx[arg_spec.arg_type][value];
    } else {
        var w = value[0];
        var h = value[1];

        // ignore the content
        // hope it does not matter
        var imageData = new ImageData(w, h);
        if (!(arg_spec.arg_type in exec_ctx)) {
            exec_ctx[arg_spec.arg_type] = [];
        }

        exec_ctx[arg_spec.arg_type].push(imageData);
        return imageData;
    }
}

function handle_one_argument(arg_spec, value,  prog_ctx, exec_ctx, gl_ctx) {

	if (arg_spec.arg_type == "String" && typeof value == "object") {

		return value[0];
	} else if (arg_spec.arg_type == "GLenum" || arg_spec.arg_type == "GLint") {
        // assert(value in gl_ctx, "the macro is not contained in gl_context");
        if (typeof value == "number") {
            // dirty hack of enums having no constraints
            // in which case, the fuzzer generate some integer values directly
            // ......
            return value;
        }

		var dot_index = value.indexOf(".");

		if (dot_index == -1) {
			return gl_ctx[value];
		} else {
			var ext_name = value.substr(0, dot_index);
			var macro_name = value.substr(dot_index + 1, value.length);

			var ext = gl_ctx.getExtension(ext_name);
			if (ext == null) {
				return null;
			}

			if (macro_name in ext) {
				return ext[macro_name];
			}

			return null;
		}
    } else if (arg_spec.arg_type.startsWith("WebGL")) {
        // WebGL* types
        // first it is possible to be null
        // the fuzzer may generate a null value for it
        // we may need to avoid it in the future.
        // if the browsers reject a null value
        if (value == null) {
            return value;
        }

        // else, it refers to a return value of a previous call
        // assert(value in exec_ctx, value + " does not have a  return value saved")
        // it should have been saved by previous calls that create them
        // here is the index of a previous call
        if (!(value in exec_ctx)) {
            return null;
        }

        return exec_ctx[value];
    } else if (arg_spec.arg_type == "ArrayBufferOrNull" || arg_spec.arg_type == "ArrayBufferViewOrNull") {
        if (typeof value == "number") {
            return exec_ctx[arg_spec.arg_type][value];
        } else if (value instanceof Array) {
            var arr = new ArrayBuffer(value);

            if (arg_spec.arg_type == "ArrayBufferOrNull") {

                if (!(arg_spec.arg_type in exec_ctx)){
                    exec_ctx[arg_spec.arg_type] = [];
                }
                exec_ctx[arg_spec.arg_type].push(arr);

                return arr;
            } else if (arg_spec.arg_type == "ArrayBufferViewOrNull"){
                // here DataView may not be the expected data type
                // by the webgl runtime
                // TODO: fix it
                // it maybe very complex
                var view = new DataView(arr);

                if (!(arg_spec.arg_type in exec_ctx)) {
                    exec_ctx[arg_spec.arg_type] = [];
                }
                exec_ctx[arg_spec.arg_type].push(view);
                return view;
            }
            return value;
        }
    } else if (arg_spec.arg_type == "ImageData") {

        return handle_imagedata_type(arg_spec, value, exec_ctx);

    } else if (arg_spec.arg_type.startsWith("HTML")){

        return handle_htmlelement_type(arg_spec, value, exec_ctx);

    } else if (arg_spec.arg_type == "OffscreenCanvas") {

        return handle_offscreencanvas_type(arg_spec, value, exec_ctx);

    } else if (arg_spec.arg_type == "ImageBitmap") {
        var ref = value["ref"];
        var v = value["value"];

        var new_arg_spec = {"arg_type":ref};

        if (ref.startsWith("HTML")) {
            return handle_htmlelement_type(new_arg_spec, v, exec_ctx);
        } else if (ref == "ImageData") {
            return handle_imagedata_type(new_arg_spec, v, exec_ctx);
        } else if (ref == "OffscreenCanvas") {
            return handle_offscreencanvas_type(new_arg_spec, v, exec_ctx);
        }

        assert(false, "unexpected type for imagebitmap");
    }

    return value;
}

function process_arguments(api_spec, arg_values, prog_ctx, exec_ctx, gl_ctx) {

    var i = 0;

    assert(api_spec.args.length === arg_values.length,
        "# of argument values not equal the the required arguments");

    var processed_args = [];
    while (i < api_spec.args.length) {

        var v = handle_one_argument(api_spec.args[i], arg_values[i], prog_ctx, exec_ctx, gl_ctx);
        processed_args[i] = v;
        i ++;
    }
    // return a list of values to pass to
    // the api
    return processed_args;
}

function test(testcase, gl_ctx, exec_ctx) {

    var res = [];
    var spec = specs[testcase.spec];
    var i = 0;

    while (i < testcase.apis.length) {

        var api = testcase.apis[i];
        // console.log("spec", spec);
        var api_spec = spec.apis[api.id];
        // console.log("api", api);
        var status = {};

        var fn = gl_ctx[api.name];
        // console.log("fn", fn);
        // console.log("api", api);
        console.log("api_spec", api_spec);
        console.log("arg_values", api.arg_values);
        var args = process_arguments(api_spec, api.arg_values, testcase.ctx, exec_ctx, gl_ctx);
        console.log("== args== ", args);

	status.ret = undefined;
	status.ex = undefined;
	status.msg = undefined;
	status.err = -1;

	// assert(api.name in gl_ctx, api.name  + " is not a supported webgl function");

	if (!(api.name in gl_ctx)) {
	    status.ex = api.name  + " is not a supported webgl function";
	} else {
	    // execute the api with args populated
            try {
		var ret = fn.apply(gl_ctx, args);
		var er1 = gl_ctx.getError();
		gl_ctx.flush();
		var er_cd = gl_ctx.getError();
		console.log("er1", er1, "er_cd", er_cd);

		// console.log("Exception did not happen");
		if (ret != undefined) {
                    exec_ctx[i] = ret;
		    status.ret = ret;
		}
		
		if (er_cd == gl_ctx.NO_ERROR) {
		    status.err = 0;
		} else if (er_cd == gl_ctx.INVALID_ENUM) {
		    status.err = "INVALID_ENUM";
		} else if (er_cd == gl_ctx.INVALID_VALUE) {
		    status.err = "INVALID_VALUE";
		} else if (er_cd == gl_ctx.INVALID_OPERATION) {
		    status.err = "INVALID_OPERATION";
		} else if (er_cd == gl_ctx.INVALID_FRAMEBUFFER_OPERATION) {
		    status.err = "INVALID_FRAMEBUFFER_OPERATION";
		} else if (er_cd == gl_ctx.OUT_OF_MEMORY) {
		    status.err = "OUT_OF_MEMORY";
		} else if (er_cd == gl_ctx.CONTEXT_LOST_WEBGL) {
		    status.err = "CONTEXT_LOST_WEBGL";
		} else {
		    status.err = er_cd;
		}

            } catch (err) {
		status.err = {"message": err.message};
		// console.log("exception happpend");
		console.log(i, api.name, err);
		// throw "exception happened while executing " + api.name;
		status.ex = err;
            }

	    // detecting chrome browser and check whether getRuntimeMessage is defined or not
	    if (navigator.userAgent.indexOf("Chrome") !== -1 && "getRuntimeMessage" in gl_ctx)
	    {
		msg = gl_ctx.getRuntimeMessage();
		status.msg = msg;
	    }
	}

        // console.log("status", JSON.stringify(status));
        res[i] = status;
        i ++;
    }

    // console.log("res", res);
    return res;
}

function post_test(exec_ctx) {
    delete_canvas();

    var elems = exec_ctx.elements;
    var i = 0;

	if (elems != null) {
		while( i < elems.length) {
			document.body.removeChild(elems[i]);
			i ++;
		}
	}
}

var curr_test = null;

function run_a_test(testcase_str) {

    var testcase = null;

    if (typeof testcase_str == "object") {
	testcase = testcase_str;
    } else {
	try {
            testcase = JSON.parse(testcase_str);
	} catch (err) {
            return "malformated testcase";
	}
    }

    curr_test = testcase;

    console.log("testcase loaded:", testcase);


    if (testcase.test_flag == 0xab1) {
	// inject a timeout case for testing infinite execution
	// still not handled
	// not used for the moment
	while (true)
	    ;
    }
    
    
    // pre test
    // create canvas and get ctx
    // width and heigth hardcoded now
    var gl_ctx = prepare_context(testcase.spec, 600, 400);

    var exec_ctx = {};
    exec_ctx.elements = [];

    if (gl_ctx == null) {
        console.log("pretest failed");
	var ret = {};
	ret.gl_create_failure=true;
        return ret;
    }

    var res = test(testcase, gl_ctx, exec_ctx);
    post_test(exec_ctx);
    return res;
}
