#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
import nibabel as nb

from niworkflows.nipype.interfaces.ants.resampling import ApplyTransforms


class FixHeaderApplyTransforms(ApplyTransforms):
    """
    A replacement for nipype.interfaces.ants.resampling.ApplyTransforms that
    fixes the resampled image header to match the xform of the reference
    image
    """

    def _run_interface(self, runtime, correct_return_codes=(0,)):
        # Run normally
        runtime = super(FixHeaderApplyTransforms, self)._run_interface(
            runtime, correct_return_codes)

        # Read in reference and output
        out_file = os.path.abspath(self.inputs.output_image)
        orig = nb.load(self.inputs.reference_image)
        resampled = nb.load(out_file)

        # Copy xform infos
        qform, qform_code = orig.header.get_qform(coded=True)
        sform, sform_code = orig.header.get_sform(coded=True)
        header = resampled.header.copy()
        header.set_qform(qform, int(qform_code))
        header.set_qform(sform, int(sform_code))
        header['descrip'] = 'header fixed after ants.ApplyTransforms'

        newimg = resampled.__class__(resampled.get_data(), orig.affine, header)
        newimg.to_filename(out_file)
        return runtime
