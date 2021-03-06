"use strict";

// Load plugins
var concat = require('gulp-concat');
const autoprefixer = require("gulp-autoprefixer");
const browsersync = require("browser-sync").create();
const cleanCSS = require("gulp-clean-css");
const del = require("del");
const gulp = require("gulp");
const header = require("gulp-header");
const merge = require("merge-stream");
const plumber = require("gulp-plumber");
const rename = require("gulp-rename");
const sass = require("gulp-sass");
const uglify = require("gulp-uglify");

const DEST_ROOT = "../track19/static"

// Load package.json for banner
const pkg = require('./package.json');

// Set the banner content
const banner = ['/*!\n',
    ' * <%= pkg.title %> v<%= pkg.version %> (<%= pkg.homepage %>)\n',
    ' * Copyright 2020 -' + (new Date()).getFullYear(), ' <%= pkg.author %>\n',
    ' * Licensed under <%= pkg.license %>',
    ' */\n',
    '\n'
].join('');

// BrowserSync
function browserSync(done) {
    // browsersync.init({
    //   server: {
    //     baseDir: DEST_ROOT
    //   },
    //   port: 3000
    // });
    done();
}

// BrowserSync reload
function browserSyncReload(done) {
    browsersync.reload();
    done();
}

// Clean vendor
function clean() {
    return del([DEST_ROOT + "/vendor/"], {"force": true});
}

// Bring third party dependencies from node_modules into vendor directory
function modules() {
    return merge(
        gulp.src([
            './node_modules/jquery/dist/*',
            '!./node_modules/jquery/dist/core.js'
        ]).pipe(gulp.dest(DEST_ROOT + '/vendor/jquery')),

        gulp.src(
            './node_modules/chart.js/dist/*.js'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor/chart.js')),

        gulp.src(
            './node_modules/underscore/*.js'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor/underscore')),

        gulp.src(
            './node_modules/bootstrap/dist/js/*'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor/bootstrap/js')),

        gulp.src(
            './node_modules/bootstrap/scss/**/*'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor/bootstrap/scss')),

        // gulp.src(
        //     './node_modules/@panzoom/panzoom/dist/panzoom.js'
        // ).pipe(gulp.dest(DEST_ROOT + '/vendor/panzoom.js')),

        gulp.src(
            './node_modules/@fortawesome/**/*'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor')),

        gulp.src(
            './node_modules/jquery.easing/*.js'
        ).pipe(gulp.dest(DEST_ROOT + '/vendor/jquery-easing')),

        gulp.src([
            './node_modules/datatables.net/js/*.js',
            './node_modules/datatables.net-bs4/js/*.js',
            './node_modules/datatables.net-bs4/css/*.css'
        ]).pipe(gulp.dest(DEST_ROOT + '/vendor/datatables')),
    );
}

// CSS task
function css() {
    return gulp
        .src("./scss/**/*.scss")
        .pipe(plumber())
        .pipe(sass({
            outputStyle: "expanded",
            includePaths: "./node_modules",
        }))
        .on("error", sass.logError)
        .pipe(autoprefixer({
            cascade: false
        }))
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(gulp.dest(DEST_ROOT + "/css"))
        .pipe(rename({
            suffix: ".min"
        }))
        .pipe(cleanCSS())
        .pipe(gulp.dest(DEST_ROOT + "/css"))
        .pipe(browsersync.stream());
}

// JS task
function js() {
    return gulp
        .src([
            './js/typeahead.0.11.1.js',
            './node_modules/@panzoom/panzoom/dist/panzoom.js',
            // './js/chart-area-demo.js',
            // './js/chart-bar-demo.js',
            // './js/chart-pie-demo.js',
            // './js/datatables-demo.js',
            './js/track19_form.js',
            './js/track19_chart.js',
        ])
        // .pipe(uglify())
        .pipe(header(banner, {
            pkg: pkg
        }))
        .pipe(concat('track19.all.js'))
        .pipe(rename({
            suffix: '.min'
        }))
        .pipe(gulp.dest(DEST_ROOT + '/js'))
        .pipe(browsersync.stream());
}

// Watch files
function watchFiles() {
    gulp.watch("./scss/**/*", css);
    gulp.watch(["./js/**/*", "!./js/**/*.min.js"], js);
    gulp.watch("./**/*.html", browserSyncReload);
}

// Define complex tasks
const vendor = gulp.series(clean, modules);
const build = gulp.series(vendor, gulp.parallel(css, js));
const watch = gulp.series(build, gulp.parallel(watchFiles, browserSync));

// Export tasks
exports.css = css;
exports.js = js;
exports.clean = clean;
exports.vendor = vendor;
exports.build = build;
exports.watch = watch;
exports.default = build;
