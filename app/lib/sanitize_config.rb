# frozen_string_literal: true

class Sanitize
  module Config
    HTTP_PROTOCOLS ||= ['http', 'https', 'dat', 'dweb', 'ipfs', 'ipns', 'ssb', 'gopher', :relative].freeze

    CLASS_WHITELIST_TRANSFORMER = lambda do |env|
      node = env[:node]
      class_list = node['class']&.split(/[\t\n\f\r ]/)

      return unless class_list

      class_list.keep_if do |e|
        return true if e =~ /^(h|p|u|dt|e)-/ # microformats classes
        return true if e =~ /^(mention|hashtag)$/ # semantic classes
        return true if e =~ /^(thought_bubble|speech_bubble|out_of_character)$/ #rp classes
        return true if e =~ /^(ellipsis|invisible)$/ # link formatting classes
        return true if e =~ /^bbcode__([a-z2-5\-]+)$/ # bbcode
      end

      node['class'] = class_list.join(' ')
    end

    MASTODON_STRICT ||= freeze_config(
      elements: %w(p br hr span s a b u del blockquote code em strong h1 h2 h3 h4 h5 h6 ol ul li pre code sub sup strike mark img),

      attributes: {
        'a'    => %w(href rel class alt title),
        'span' => %w(class data-bbcodesize data-bbcodecolor),
        'p'    => %w(class),
      },

      add_attributes: {
        'a' => {
          'rel' => 'nofollow noopener',
          'target' => '_blank',
        },
      },

      protocols: {
        'a' => { 'href' => HTTP_PROTOCOLS },
      },

      transformers: [
        CLASS_WHITELIST_TRANSFORMER,
      ]
    )

    MASTODON_OEMBED ||= freeze_config merge(
      RELAXED,
      elements: RELAXED[:elements] + %w(audio embed iframe source video),

      attributes: merge(
        RELAXED[:attributes],
        'audio'  => %w(controls),
        'embed'  => %w(height src type width),
        'iframe' => %w(allowfullscreen frameborder height scrolling src width),
        'source' => %w(src type),
        'video'  => %w(controls height loop width),
        'div'    => [:data]
      ),

      protocols: merge(
        RELAXED[:protocols],
        'embed'  => { 'src' => HTTP_PROTOCOLS },
        'iframe' => { 'src' => HTTP_PROTOCOLS },
        'source' => { 'src' => HTTP_PROTOCOLS }
      )
    )
  end
end
