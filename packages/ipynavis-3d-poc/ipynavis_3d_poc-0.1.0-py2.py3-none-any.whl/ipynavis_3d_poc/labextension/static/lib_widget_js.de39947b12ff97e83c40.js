(self["webpackChunkipynavis_3d_poc"] = self["webpackChunkipynavis_3d_poc"] || []).push([["lib_widget_js"],{

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) CristianI
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;
//# sourceMappingURL=version.js.map

/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// Copyright (c) CristianI
// Distributed under the terms of the Modified BSD License.
var __awaiter = (this && this.__awaiter) || function (thisArg, _arguments, P, generator) {
    function adopt(value) { return value instanceof P ? value : new P(function (resolve) { resolve(value); }); }
    return new (P || (P = Promise))(function (resolve, reject) {
        function fulfilled(value) { try { step(generator.next(value)); } catch (e) { reject(e); } }
        function rejected(value) { try { step(generator["throw"](value)); } catch (e) { reject(e); } }
        function step(result) { result.done ? resolve(result.value) : adopt(result.value).then(fulfilled, rejected); }
        step((generator = generator.apply(thisArg, _arguments || [])).next());
    });
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.SatelliteMonitorView = exports.SatelliteMonitorModel = exports.ExampleView = exports.ExampleModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
// Import the CSS
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
class ExampleModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: ExampleModel.model_name, _model_module: ExampleModel.model_module, _model_module_version: ExampleModel.model_module_version, _view_name: ExampleModel.view_name, _view_module: ExampleModel.view_module, _view_module_version: ExampleModel.view_module_version, value: 'Hello World' });
    }
}
exports.ExampleModel = ExampleModel;
ExampleModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
ExampleModel.model_name = 'ExampleModel';
ExampleModel.model_module = version_1.MODULE_NAME;
ExampleModel.model_module_version = version_1.MODULE_VERSION;
ExampleModel.view_name = 'ExampleView'; // Set to null if no view
ExampleModel.view_module = version_1.MODULE_NAME; // Set to null if no view
ExampleModel.view_module_version = version_1.MODULE_VERSION;
class ExampleView extends base_1.DOMWidgetView {
    render() {
        this.el.classList.add('custom-widget');
        this.value_changed();
        this.model.on('change:value', this.value_changed, this);
    }
    value_changed() {
        this.el.textContent = this.model.get('value');
    }
}
exports.ExampleView = ExampleView;
const core_1 = __webpack_require__(/*! @babylonjs/core */ "./node_modules/@babylonjs/core/index.js");
const gui_1 = __webpack_require__(/*! @babylonjs/gui */ "webpack/sharing/consume/default/@babylonjs/gui/@babylonjs/gui");
__webpack_require__(/*! @babylonjs/loaders */ "./node_modules/@babylonjs/loaders/index.js");
class SatelliteMonitorModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: SatelliteMonitorModel.model_name, _model_module: SatelliteMonitorModel.model_module, _model_module_version: SatelliteMonitorModel.model_module_version, _view_name: SatelliteMonitorModel.view_name, _view_module: SatelliteMonitorModel.view_module, _view_module_version: SatelliteMonitorModel.view_module_version, 
            // user input
            satellites: [], width: 800, height: 600, 
            // meshes
            earthMeshPath: SatelliteMonitorModel.earthMesh.default, satelliteMeshPath: SatelliteMonitorModel.satelliteMesh.default });
    }
}
exports.SatelliteMonitorModel = SatelliteMonitorModel;
SatelliteMonitorModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
SatelliteMonitorModel.model_name = 'SatelliteMonitorModel';
SatelliteMonitorModel.model_module = version_1.MODULE_NAME;
SatelliteMonitorModel.model_module_version = version_1.MODULE_VERSION;
SatelliteMonitorModel.view_name = 'SatelliteMonitorView';
SatelliteMonitorModel.view_module = version_1.MODULE_NAME;
SatelliteMonitorModel.view_module_version = version_1.MODULE_VERSION;
SatelliteMonitorModel.earthMesh = __webpack_require__(/*! file-loader!./meshes/earth_good.glb */ "./node_modules/file-loader/dist/cjs.js!./lib/meshes/earth_good.glb");
SatelliteMonitorModel.satelliteMesh = __webpack_require__(/*! file-loader!./meshes/satellite.glb */ "./node_modules/file-loader/dist/cjs.js!./lib/meshes/satellite.glb");
class SatelliteMonitorView extends base_1.DOMWidgetView {
    render() {
        var _a;
        return __awaiter(this, void 0, void 0, function* () {
            yield this.createBasicScene();
            yield this.plotSatellites();
            this.createGUI();
            this.createCamera();
            (_a = this.engine) === null || _a === void 0 ? void 0 : _a.runRenderLoop(() => {
                var _a;
                (_a = this.scene) === null || _a === void 0 ? void 0 : _a.render();
            });
        });
    }
    createBasicScene() {
        return __awaiter(this, void 0, void 0, function* () {
            this.canvas = document.createElement('canvas');
            this.canvas.width = this.model.get('width');
            this.canvas.height = this.model.get('height');
            this.el.appendChild(this.canvas);
            this.engine = new core_1.Engine(this.canvas, true, { stencil: true });
            this.scene = new core_1.Scene(this.engine);
            this.scene.clearColor = new core_1.Color4(0, 0, 0, 1);
            new core_1.AxesViewer(this.scene, 13);
            new core_1.HemisphericLight('light', new core_1.Vector3(0, -15, 0), this.scene).intensity = 5;
            this.earth = (yield core_1.SceneLoader.ImportMeshAsync('', this.model.get('earthMeshPath'), '', this.scene)).meshes[0];
            this.earth.position = core_1.Vector3.Zero();
            this.earth.rotate(new core_1.Vector3(0, 1, 0), core_1.Tools.ToRadians(180));
        });
    }
    createGUI() {
        const gui = gui_1.AdvancedDynamicTexture.CreateFullscreenUI("gui", true, this.scene);
        const rightPanel = new gui_1.StackPanel("rightPanel");
        rightPanel.width = "40px";
        rightPanel.top = "10px";
        rightPanel.isVertical = true;
        rightPanel.horizontalAlignment = gui_1.Control.HORIZONTAL_ALIGNMENT_RIGHT;
        rightPanel.verticalAlignment = gui_1.Control.VERTICAL_ALIGNMENT_TOP;
        const exitButton = gui_1.Button.CreateSimpleButton("exitButton", "x");
        exitButton.width = "30px";
        exitButton.height = "30px";
        exitButton.color = "red";
        exitButton.onPointerClickObservable.add((value) => {
            var _a;
            (_a = this.engine) === null || _a === void 0 ? void 0 : _a.stopRenderLoop();
            this.canvas.remove();
        });
        gui.addControl(rightPanel);
        rightPanel.addControl(exitButton);
    }
    createCamera() {
        this.camera = new core_1.ArcRotateCamera('camera', core_1.Tools.ToRadians(45), core_1.Tools.ToRadians(90), 18, core_1.Vector3.Zero(), this.scene);
        this.camera.attachControl();
    }
    plotSatellites() {
        return __awaiter(this, void 0, void 0, function* () {
            this.satellites = this.model.get('satellites');
            if (this.satellites.length == 0) {
                return;
            }
            const satelliteMeshes = [];
            satelliteMeshes.push((yield core_1.SceneLoader.ImportMeshAsync("", "", this.model.get('satelliteMeshPath'), this.scene)).meshes[0]);
            for (let i = 1; i < this.satellites.length; i++) {
                satelliteMeshes.push(satelliteMeshes[0].clone("satellite" + i, null));
            }
            for (let i = 0; i < this.satellites.length; i++) {
                const currentSatellite = this.satellites[i];
                const currentSatelliteMesh = satelliteMeshes[i];
                currentSatellite.mesh = currentSatelliteMesh;
                console.log("Loading mesh: " + currentSatelliteMesh.name + " for satellite: " + currentSatellite.name);
                //this.earth.addChild(currentSatelliteMesh)
                currentSatelliteMesh.position = new core_1.Vector3(currentSatellite.x, currentSatellite.y, currentSatellite.z);
                currentSatelliteMesh.lookAt(core_1.Vector3.Zero());
                currentSatelliteMesh.getChildMeshes()[0].renderOutline = true;
                currentSatelliteMesh.getChildMeshes()[0].outlineColor = core_1.Color3.White();
            }
        });
    }
}
exports.SatelliteMonitorView = SatelliteMonitorView;
//# sourceMappingURL=widget.js.map

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./css/widget.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/widget.css ***!
  \**************************************************************/
/***/ ((module, exports, __webpack_require__) => {

// Imports
var ___CSS_LOADER_API_IMPORT___ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
exports = ___CSS_LOADER_API_IMPORT___(false);
// Module
exports.push([module.id, ".custom-widget {\n  background-color: lightseagreen;\n  padding: 0px 2px;\n}\n", ""]);
// Exports
module.exports = exports;


/***/ }),

/***/ "./node_modules/file-loader/dist/cjs.js!./lib/meshes/earth_good.glb":
/*!**************************************************************************!*\
  !*** ./node_modules/file-loader/dist/cjs.js!./lib/meshes/earth_good.glb ***!
  \**************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__webpack_require__.p + "06457057fe1b7626859fcc5a69a9c7afc5801ec24b6bc326fd3ade74d929d02d.glb");

/***/ }),

/***/ "./node_modules/file-loader/dist/cjs.js!./lib/meshes/satellite.glb":
/*!*************************************************************************!*\
  !*** ./node_modules/file-loader/dist/cjs.js!./lib/meshes/satellite.glb ***!
  \*************************************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (__webpack_require__.p + "c222aac9d460adda754ee2f97fba1e34411f10e2b8ca7ca4b9219a50fd476d27.glb");

/***/ }),

/***/ "./css/widget.css":
/*!************************!*\
  !*** ./css/widget.css ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./widget.css */ "./node_modules/css-loader/dist/cjs.js!./css/widget.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"ipynavis-3d-poc","version":"0.1.3","description":"A Custom Jupyter Widget Library","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","dist/*.glb","css/*.css"],"homepage":"https://github.com/Thales/ipynavis-3d-poc","bugs":{"url":"https://github.com/Thales/ipynavis-3d-poc/issues"},"license":"BSD-3-Clause","author":{"name":"CristianI","email":""},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/Thales/ipynavis-3d-poc"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf ipynavis_3d_poc/labextension","clean:nbextension":"rimraf ipynavis_3d_poc/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@babylonjs/gui":"^5.12.1","@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@babylonjs/core":"^5.12.0","@babylonjs/loaders":"^5.12.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@types/jest":"^26.0.0","@types/node":"^18.0.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","copy-webpack-plugin":"^11.0.0","css-loader":"^3.2.0","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.61.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"ipynavis_3d_poc/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js.de39947b12ff97e83c40.js.map