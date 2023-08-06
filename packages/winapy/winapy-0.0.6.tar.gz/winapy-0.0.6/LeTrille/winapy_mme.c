/*
    WinAPY - Windows API wrapper in C developed for Python.
    Copyright (c) 2022 Itzsten
*/

#include "Python.h"
#include <Windows.h>
#include <stdio.h>
#include <mmeapi.h>

#pragma comment(lib, "Winmm.lib")

#if PY_MAJOR_VERSION >= 3
#define PyString_ToCharArr PyUnicode_AsUTF8
#else
#define PyString_ToCharArr PyString_AsString
#endif

BOOL WINAPI RaiseExceptionCheck(BOOL bSuccess) {
    if (GetLastError() && (!bSuccess)) {
        PyErr_SetFromWindowsErr(GetLastError());
        return TRUE;
    }
    return FALSE;
}

BOOL WINAPI ErrorCheckMME(MMRESULT ret) {
    if (!ret) {
        return FALSE;
    }
    if (ret == MMSYSERR_ALLOCATED) PyErr_SetString(PyExc_MemoryError, "Specified resource is already allocated.");
    if (ret == MMSYSERR_BADDEVICEID) PyErr_SetString(PyExc_ValueError, "Specified device identifier is out of range.");
    if (ret == MMSYSERR_NODRIVER) PyErr_SetString(PyExc_SystemError, "No device driver is present.");
    if (ret == MMSYSERR_NOMEM) PyErr_SetString(PyExc_MemoryError, "Unable to allocate or lock memory.");
    if (ret == MMSYSERR_NOMEM) PyErr_SetString(PyExc_ValueError, "Attempted to open with an unsupported waveform-audio format.");
    if (ret == WAVERR_SYNC) PyErr_SetString(PyExc_StopAsyncIteration, "The device is synchronous but waveOutOpen was called without using the WAVE_ALLOWSYNC flag.");
    if (ret == MMSYSERR_INVALHANDLE) PyErr_SetString(PyExc_TypeError, "Specified device handle is invalid.");
    if (ret == WAVERR_UNPREPARED) PyErr_SetString(PyExc_ValueError, "The data block pointed to by the pwh parameter hasn't been prepared.");
    if (ret == WAVERR_STILLPLAYING) PyErr_SetString(PyExc_TimeoutError, "There are still buffers in the queue.");
    if (ret == MMSYSERR_NOTSUPPORTED) PyErr_SetString(PyExc_ValueError, "Specified device is synchronous and does not support pausing.");
    return TRUE;
}

static PyObject* PywaveOutOpen(PyObject* self, PyObject* args) {
    //@description@ Opens the given waveform-audio output device for playback. The return value specifies a handle identifying the open waveform-audio output device.@@HWAVEOUT
    //@args@ deviceID|int|Identifier of the waveform-audio output device to open. It can be either a device identifier or a handle of an open waveform-audio input device. You can also use the following flag instead of a device identifier;<br><b>WAVE_MAPPER</b> - The function selects a waveform-audio output device capable of playing the given format.@@wfx|tuple|A tuple of 6 integers representing the values below;<br><ul><li><b>wFormatTag</b><br>Waveform-audio format type. Format tags are registered with Microsoft Corporation for many compression algorithms. For one- or two-channel PCM data, this value should be WAVE_FORMAT_PCM.<br></li><li><b>nChannels</b><br>Number of channels in the waveform-audio data. Monaural data uses one channel and stereo data uses two channels.<br></li><li><b>nSamplesPerSec</b><br>Sample rate, in samples per second (hertz). If wFormatTag is WAVE_FORMAT_PCM, then common values for nSamplesPerSec are 8.0 kHz, 11.025 kHz, 22.05 kHz, and 44.1 kHz. For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br></li><li><b>nAvgBytesPerSec</b><br>Required average data-transfer rate, in bytes per second, for the format tag. If wFormatTag is WAVE_FORMAT_PCM, nAvgBytesPerSec should be equal to the product of nSamplesPerSec and nBlockAlign. For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br></li><li><b>nBlockAlign</b><br>Block alignment, in bytes. The block alignment is the minimum atomic unit of data for the wFormatTag format type. If wFormatTag is WAVE_FORMAT_PCM or WAVE_FORMAT_EXTENSIBLE, nBlockAlign must be equal to the product of nChannels and wBitsPerSample divided by 8 (bits per byte). For non-PCM formats, this member must be computed according to the manufacturer's specification of the format tag.<br><br>Software must process a multiple of nBlockAlign bytes of data at a time. Data written to and read from a device must always start at the beginning of a block. For example, it is illegal to start playback of PCM data in the middle of a sample (that is, on a non-block-aligned boundary).<br></li><li><b>wBitsPerSample</b><br>Bits per sample for the wFormatTag format type. If wFormatTag is WAVE_FORMAT_PCM, then wBitsPerSample should be equal to 8 or 16. For non-PCM formats, this member must be set according to the manufacturer's specification of the format tag. If wFormatTag is WAVE_FORMAT_EXTENSIBLE, this value can be any integer multiple of 8 and represents the container size, not necessarily the sample size; for example, a 20-bit sample size is in a 24-bit container. Some compression schemes cannot define a value for wBitsPerSample, so this member can be 0.<br></li></ul>@@callback|int|Specifies the callback mechanism, or None.@@instance|int|User-instance data passed to the callback mechanism. This parameter is not used with the window callback mechanism.@@fOpen|int|<ul><li><b>CALLBACK_EVENT</b><br>The dwCallback parameter is an event handle.<br></li><li><b>CALLBACK_NULL</b><br> No callback mechanism. This is the default setting.<br></li><li><b>CALLBACK_THREAD</b><br> The dwCallback parameter is a thread identifier.<br></li><li><b>CALLBACK_WINDOW</b><br> The dwCallback parameter is a window handle.<br></li><li><b>WAVE_ALLOWSYNC</b><br> If this flag is specified, a synchronous waveform-audio device can be opened. If this flag is not specified while opening a synchronous driver, the device will fail to open.<br></li><li><b>WAVE_MAPPED_DEFAULT_COMMUNICATION_DEVICE</b><br> If this flag is specified and the uDeviceID parameter is WAVE_MAPPER, the function opens the default communication device. This flag applies only when uDeviceID equals WAVE_MAPPER. (Requires Windows 7)<br></li><li><b>WAVE_FORMAT_DIRECT</b><br> If this flag is specified, the ACM driver does not perform conversions on the audio data.<br></li><li><b>WAVE_FORMAT_QUERY</b><br> If this flag is specified, waveOutOpen queries the device to determine if it supports the given format, but the device is not actually opened.<br></li><li><b>WAVE_MAPPED</b><br> If this flag is specified, the uDeviceID parameter specifies a waveform-audio device to be mapped to by the wave mapper.<br></li></ul>
    PyObject* obOut;
    UINT deviceId;
    WAVEFORMATEX wFormat;
    DWORD_PTR dwCallback = 0, dwInstance = 0;
    DWORD fdwOpen = CALLBACK_NULL;
    HWAVEOUT hOut = 0;
    PyObject* pyPe = Py_None;
    
    if (!PyArg_ParseTuple(args, "k(HHkkHH)|OKk",
        &deviceId,
        &wFormat.wFormatTag, &wFormat.nChannels, &wFormat.nSamplesPerSec,
        &wFormat.nAvgBytesPerSec, &wFormat.nBlockAlign, &wFormat.wBitsPerSample,
        &pyPe,
        &dwInstance,
        &fdwOpen
    )) return NULL;

    if (pyPe != Py_None) {
        dwCallback = PyLong_AsUnsignedLongLong(pyPe);
    }
    
    MMRESULT res = waveOutOpen(&hOut, deviceId, &wFormat, dwCallback, dwInstance, fdwOpen);
    
    if (ErrorCheckMME(res)) return NULL;
    return Py_BuildValue("L", hOut);
}

static PyObject* PywaveOutPrepareHeader(PyObject* self, PyObject* args) {
    //@description@ The waveOutPrepareHeader function prepares a waveform-audio data block for playback. The return value should be used as the new wave header, as it is prepared for playback.@@tuple
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|Tuple that identifies the data block to be prepared. Must contain the followings values;<br><ul><li>The data block to be prepared, as a <b>bytearray</b> object.</li><li>When the header is used in input, specifies how much data is in the buffer. If it is not used in input, set this value to 0.</li><li>User data, or 0.</li><li>A bitwise OR of zero of more flags.</li><li>Number of times to play the loop. This member is used only with output buffers. Zero if unused</li></ul>
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }
    
    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }

    MMRESULT res = waveOutPrepareHeader(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_BuildValue("(OkKkk)", 
        PyByteArray_FromStringAndSize(hdr.lpData, length),
        hdr.dwBytesRecorded,
        hdr.dwUser,
        hdr.dwFlags,
        hdr.dwLoops);
}

static PyObject* PywaveOutClose(PyObject* self, PyObject* args) {
    //@description@ Closes and frees memory from the specified waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutClose(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutUnprepareHeader(PyObject* self, PyObject* args) {
    //@description@ Frees memory from the specified header and waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|The header to be freen
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }

    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }
    MMRESULT res = waveOutUnprepareHeader(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PywaveOutWrite(PyObject* self, PyObject* args) {
    //@description@ Sends a data block to the given waveform-audio output device.@@bool
    //@args@ hwo|HWAVEOUT|Handle to the waveform-audio output device.@@hdr|tuple|The header containing the data block to be sent. For more information, please look under the waveOutPrepareHeader function.
    HWAVEOUT hwo;
    WAVEHDR hdr;
    UINT cbwh = sizeof(WAVEHDR);
    PyObject* obData;

    if (!PyArg_ParseTuple(args, "L(OkKkk)",
        &hwo,
        &obData,
        &hdr.dwBytesRecorded,
        &hdr.dwUser,
        &hdr.dwFlags,
        &hdr.dwLoops
    )) return NULL;

    if (!PyByteArray_Check(obData)) {
        PyErr_SetString(PyExc_TypeError, "argument 2: index 1: Excepted bytes type object");
        return NULL;
    }

    LONGLONG length = PyByteArray_Size(obData);

    hdr.dwBufferLength = length;
    hdr.lpData = PyByteArray_AsString(obData);
    hdr.lpNext = 0;
    hdr.reserved = 0;

    if (hdr.lpData == NULL) {
        PyErr_SetString(PyExc_TypeError, "Could not convert bytearray to char pointer.");
        return NULL;
    }

    MMRESULT res = waveOutWrite(hwo, &hdr, cbwh);

    if (ErrorCheckMME(res)) return NULL;
    return Py_True;
}

static PyObject* PywaveOutRestart(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutRestart(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutPause(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutPause(hwo)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutGetPitch(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetPitch(hwo, &res)))   return NULL;
    return Py_BuildValue("k", res);
}

static PyObject* PywaveOutGetPlaybackRate(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetPitch(hwo, &res)))   return NULL;
    return Py_BuildValue("k", res);
}

static PyObject* PywaveOutGetVolume(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD res;
    if (!PyArg_ParseTuple(args, "L", &hwo)) return NULL;
    if (ErrorCheckMME(waveOutGetVolume(hwo, &res)))   return NULL;
    return Py_BuildValue("HH", LOWORD(res), HIWORD(res));
}

static PyObject* PywaveOutSetPitch(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    DWORD pitch;
    if (!PyArg_ParseTuple(args, "Lk", &hwo, &pitch)) return NULL;
    if (ErrorCheckMME(waveOutSetPitch(hwo, pitch)))   return NULL;
    return Py_True;
}

static PyObject* PywaveOutSetVolume(PyObject* self, PyObject* args) {
    HWAVEOUT hwo;
    WORD left, right;
    if (!PyArg_ParseTuple(args, "LHH", &hwo, &left, &right)) return NULL;
    if (ErrorCheckMME(waveOutSetVolume(hwo, MAKELONG(left, right)))) return NULL;
    return Py_True;
}

static PyMethodDef module_methods[] = {
    { "waveOutOpen", PywaveOutOpen, METH_VARARGS },
    { "waveOutPrepareHeader", PywaveOutPrepareHeader, METH_VARARGS },
    { "waveOutClose", PywaveOutClose, METH_VARARGS },
    { "waveOutUnprepareHeader", PywaveOutUnprepareHeader, METH_VARARGS },
    { "waveOutWrite", PywaveOutWrite, METH_VARARGS },
    { "waveOutRestart", PywaveOutRestart, METH_VARARGS },
    { "waveOutPause", PywaveOutPause, METH_VARARGS },
    { "waveOutGetPitch", PywaveOutGetPitch, METH_VARARGS },
    { "waveOutGetPlaybackRate", PywaveOutGetPlaybackRate, METH_VARARGS },
    { "waveOutGetVolume", PywaveOutGetVolume, METH_VARARGS },
    { "waveOutSetPitch", PywaveOutSetPitch, METH_VARARGS },
    { "waveOutSetVolume", PywaveOutSetVolume, METH_VARARGS },

    /* sentinel */
    { 0 }
};

static struct PyModuleDef ModuleCombinations =
{
    PyModuleDef_HEAD_INIT,
    "WinAPY_mme", /* name of module */
    NULL,
    -1,   /* size of per-interpreter state of the module, or -1 if the module keeps state in global variables. */
    module_methods
};


void PyInit_winapy_mme(void) {
    PyModule_Create(&ModuleCombinations);
}