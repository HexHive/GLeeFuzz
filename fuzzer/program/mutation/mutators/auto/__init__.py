# ******************************************************
# * Copyright (C) 2022 the GLeeFuzz authors.
# * This file is part of GLeeFuzz.
# *
# * GLeeFuzz is free software: you can redistribute it
# * and/or modify it under the terms of the GNU General 
# * Public License as published by the Free Software 
# * Foundation, either version 3 of the License, or 
# * (at your option) any later version.
# *
# * GLeeFuzz is distributed in the hope that it will 
# * be useful, but WITHOUT ANY WARRANTY; without even
# * the implied warranty of MERCHANTABILITY or FITNESS
# * FOR A PARTICULAR PURPOSE. See the GNU General 
# * Public License for more details.
# *
# * You should have received a copy of the GNU 
# * General Public License along with GLeeFuzz. If not,
# * see <https://www.gnu.org/licenses/>.
# ******************************************************

from . import activeuniformsget_active_uniforms_mutator
from . import pixelpackbufferread_pixels_mutator
from . import alignmentpixel_storei_mutator
from . import prefixbind_attrib_location_mutator
from . import arraybuffervertex_attrib_i_pointer_mutator
from . import premultiplyalphaisnttex_image_d_mutator
from . import arraybuffervertex_attrib_pointer_mutator
from . import premultiplyalphaisnttex_sub_image_d_mutator
from . import arraybufferviewread_pixels_mutator
from . import programbegin_transform_feedback_mutator
from . import arrayvertex_attribfv_mutator
from . import programget_attrib_location_mutator
from . import attributedraw_arrays_instanced_mutator
from . import programget_transform_feedback_varying_mutator
from . import attributedraw_arrays_mutator
from . import programget_uniform_location_mutator
from . import attributedraw_elements_instanced_mutator
from . import programget_uniform_mutator
from . import attributedraw_elements_mutator
from . import programlink_program_mutator
from . import attributedraw_range_elements_mutator
from . import programobjectbegin_transform_feedback_mutator
from . import attributesget_active_attrib_mutator
from . import programuniformf_mutator
from . import boundpixelunpackbuffercompressed_tex_image_d_mutator
from . import programuniformi_mutator
from . import boundpixelunpackbuffercompressed_tex_sub_image_d_mutator
from . import programuniformui_mutator
from . import boundpixelunpackbuffertex_image_d_mutator
from . import programuse_program_mutator
from . import boundpixelunpackbuffertex_sub_image_d_mutator
from . import querybegin_query_mutator
from . import buffercompressed_tex_image_d_mutator
from . import queryget_query_parameter_mutator
from . import buffercompressed_tex_sub_image_d_mutator
from . import queryobjectget_query_parameter_mutator
from . import bufferdraw_arrays_instanced_mutator
from . import queryparametersget_framebuffer_attachment_parameter_mutator
from . import bufferdraw_arrays_mutator
from . import rangebind_sampler_mutator
from . import bufferdraw_elements_instanced_mutator
from . import rangecompressed_tex_image_d_mutator
from . import bufferdraw_elements_mutator
from . import rangecompressed_tex_sub_image_d_mutator
from . import bufferdraw_range_elements_mutator
from . import rangedisable_vertex_attrib_array_mutator
from . import bufferoverflowbuffer_sub_data_mutator
from . import rangeenable_vertex_attrib_array_mutator
from . import bufferoverflowcopy_buffer_sub_data_mutator
from . import rangeget_indexed_parameter_mutator
from . import bufferread_pixels_mutator
from . import rangeget_vertex_attrib_mutator
from . import buffersdraw_buffers_mutator
from . import rangeread_pixels_mutator
from . import buffersourcecopy_buffer_sub_data_mutator
from . import rangevertex_attrib_divisor_mutator
from . import buffertex_image_d_mutator
from . import rangevertex_attrib_i_pointer_mutator
from . import buffertex_sub_image_d_mutator
from . import rangevertex_attrib_pointer_mutator
from . import charactershader_source_mutator
from . import readbufferread_buffer_mutator
from . import colorattachmentiextdraw_buffers_mutator
from . import renderbufferboundget_renderbuffer_parameter_mutator
from . import commentsshader_source_mutator
from . import renderbufferframebuffer_renderbuffer_mutator
from . import contextdelete_vertex_array_mutator
from . import shaderattach_shader_mutator
from . import databuffer_data_mutator
from . import shaderattachmentattach_shader_mutator
from . import destinationarraybufferviewread_pixels_mutator
from . import shaderdetach_shader_mutator
from . import destinationread_pixels_mutator
from . import srclengthoverridecompressed_tex_image_d_mutator
from . import dimensionsread_pixels_mutator
from . import srclengthoverridecompressed_tex_sub_image_d_mutator
from . import elementbufferdestinationcopy_buffer_sub_data_mutator
from . import srcoffsetcompressed_tex_image_d_mutator
from . import errorget_uniform_mutator
from . import srcoffsetcompressed_tex_sub_image_d_mutator
from . import feedbackbuffersbegin_transform_feedback_mutator
from . import targetbegin_query_mutator
from . import flagsclient_wait_sync_mutator
from . import targetqueryend_query_mutator
from . import flagsfence_sync_mutator
from . import targetsbind_texture_mutator
from . import flagswait_sync_mutator
from . import texturesbind_texture_mutator
from . import flipytex_image_d_mutator
from . import texturestex_image_d_mutator
from . import flipytex_sub_image_d_mutator
from . import texturestex_sub_image_d_mutator
from . import framebufferboundframebuffer_renderbuffer_mutator
from . import texturetypeframebuffer_texture_layer_mutator
from . import framebufferboundframebuffer_texture_d_mutator
from . import textureunitbind_sampler_mutator
from . import framebufferboundframebuffer_texture_layer_mutator
from . import timeoutclient_wait_sync_mutator
from . import framebufferboundget_framebuffer_attachment_parameter_mutator
from . import timeoutwait_sync_mutator
from . import indexdisable_vertex_attrib_array_mutator
from . import transformfeedbackbegin_transform_feedback_mutator
from . import indexenable_vertex_attrib_array_mutator
from . import transformfeedbackbind_buffer_base_mutator
from . import indexget_active_uniforms_mutator
from . import transformfeedbackbind_transform_feedback_mutator
from . import indexget_indexed_parameter_mutator
from . import transformfeedbackobjectdelete_transform_feedback_mutator
from . import indexget_transform_feedback_varying_mutator
from . import transformfeedbackobjectslink_program_mutator
from . import indexget_vertex_attrib_mutator
from . import transformfeedbackuse_program_mutator
from . import indexvertex_attrib_divisor_mutator
from . import transformfeedbackvaryingsbegin_transform_feedback_mutator
from . import indexvertex_attrib_i_pointer_mutator
from . import typebegin_query_mutator
from . import indexvertex_attrib_pointer_mutator
from . import typebind_texture_mutator
from . import lengthbuffer_data_mutator
from . import typebyteread_pixels_mutator
from . import lengthbuffer_sub_data_mutator
from . import typefloatread_pixels_mutator
from . import locationuniformf_mutator
from . import typeget_uniform_mutator
from . import locationuniformi_mutator
from . import typehalffloatoesread_pixels_mutator
from . import locationuniformui_mutator
from . import typehalffloatread_pixels_mutator
from . import maskclear_mutator
from . import typeintread_pixels_mutator
from . import maxclientwaittimeoutwebglclient_wait_sync_mutator
from . import typeread_pixels_mutator
from . import maxcolorattachmentsread_buffer_mutator
from . import typeunsignedbyteread_pixels_mutator
from . import numberdraw_buffers_mutator
from . import typeunsignedintread_pixels_mutator
from . import objectdelete_vertex_array_mutator
from . import typeunsignedshortread_pixels_mutator
from . import opaqueframebufferboundframebuffer_renderbuffer_mutator
from . import uniformblockindexget_active_uniform_block_name_mutator
from . import opaqueframebufferboundframebuffer_texture_d_mutator
from . import uniformlocationget_uniform_mutator
from . import opaqueframebufferboundframebuffer_texture_layer_mutator
from . import uniformsget_active_uniform_mutator
from . import opaqueframebufferdelete_framebuffer_mutator
from . import uniformsget_uniform_mutator
from . import opaqueframebufferget_framebuffer_attachment_parameter_mutator
from . import unpackcolorspaceconversionwebglpixel_storei_mutator
from . import parameterpixel_storei_mutator
from . import valuepixel_storei_mutator
from . import pbotex_image_d_mutator
from . import varyingstransform_feedback_varyings_mutator
from . import pbotex_sub_image_d_mutator
from . import zfardepth_range_mutator
from . import pixelpackbufferboundread_pixels_mutator